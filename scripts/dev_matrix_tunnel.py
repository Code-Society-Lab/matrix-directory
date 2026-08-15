import json
import os
import re
import signal
import subprocess
import sys
import urllib.request
from pathlib import Path

ENV_FILE = Path(".env")
MAS_REGISTRATION_URL = "https://account.matrix.org/oauth2/registration"
TUNNEL_TARGET = "http://localhost:5173"
URL_PATTERN = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


def update_env(values: dict[str, str]) -> None:
    existing = ENV_FILE.read_text() if ENV_FILE.exists() else ""
    lines = existing.splitlines()
    replaced = set()
    output = []

    for line in lines:
        key = line.split("=", 1)[0] if "=" in line else None

        if key in values:
            output.append(f"{key}={values[key]}")
            replaced.add(key)
        else:
            output.append(line)

    for key, value in values.items():
        if key not in replaced:
            output.append(f"{key}={value}")

    temp = ENV_FILE.with_suffix(".tmp")
    temp.write_text("\n".join(output) + "\n")
    temp.replace(ENV_FILE)


def register_client(base_url: str) -> dict:
    payload = {
        "client_name": "Matrix Directory (local)",
        "client_uri": base_url,
        "redirect_uris": [f"{base_url}/api/auth/matrix/callback"],
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "client_secret_basic",
    }

    request = urllib.request.Request(
        MAS_REGISTRATION_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        return json.load(response)


def main() -> None:
    tunnel = subprocess.Popen(
        ["cloudflared", "tunnel", "--no-autoupdate", "--url", TUNNEL_TARGET],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        tunnel_url = None

        for line in tunnel.stdout or []:
            match = URL_PATTERN.search(line)
            if match:
                tunnel_url = match.group(0)
                break

        if tunnel_url is None:
            raise RuntimeError("Could not find the Cloudflare tunnel URL")

        print(f"Tunnel: {tunnel_url}")
        print("Registering OAuth client…")

        client = register_client(tunnel_url)

        update_env(
            {
                "FRONTEND_ORIGIN": tunnel_url,
                "MATRIX_OIDC_CLIENT_ID": client["client_id"],
                "MATRIX_OIDC_CLIENT_SECRET": client["client_secret"],
                "MATRIX_OIDC_REDIRECT_URI": (f"{tunnel_url}/api/auth/matrix/callback"),
                "SESSION_COOKIE_SECURE": "true",
            }
        )

        print("Updated .env")
        subprocess.run(["docker", "compose", "up", "-d", "--build"], check=True)
        print(f"Open {tunnel_url}")

        tunnel.wait()

    except KeyboardInterrupt:
        pass
    finally:
        tunnel.send_signal(signal.SIGTERM)
        tunnel.wait()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
