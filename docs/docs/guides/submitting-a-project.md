# Submit a project

Authenticated users can publish Matrix bots, SDKs, plugins, integrations, and
other ecosystem projects directly from the directory.

## Publish a listing

1. Sign in to Matrix Directory.
2. Open your dashboard and select **Add listing**.
3. Enter the project name, short description, and Markdown description.
4. Provide at least one repository or website.
5. Choose exactly one project type.
6. Optionally choose labels and provide a Matrix room.
7. Indicate whether the project operates in end-to-end encrypted rooms.
8. Review the preview and select **Publish listing**.

The listing is associated with the authenticated account and the application
redirects to its public page after publication.

## Types and labels

A project type describes what the project **is**. Every listing has exactly
one of the initial directory types: **Bot**, **SDK**, **Framework**,
**Bridges**, **Clients**, **Server**, or **Integrations**.

Labels describe what the project **does**. A listing may have any number of
labels, including none. Examples include **Dev tools** and **Utility**.

This separation lets visitors filter by both the project format and its
purpose.

## Field requirements

| Field | Requirement |
| --- | --- |
| Name | Required; 2–100 characters |
| Short description | Required; 1–160 characters |
| About | Required; 1–10,000 characters; Markdown supported |
| Repository | Required when no website is supplied |
| Website | Required when no repository is supplied |
| Matrix room | Optional |
| Project type | Exactly one required |
| Labels | Optional; duplicate labels are rejected |
| E2EE support | Select when the project operates in encrypted Matrix rooms |

URLs must be absolute `http://` or `https://` URLs no longer than 255
characters.

!!! note "Listings are public"
    Do not include secrets, access tokens, private room links, or other
    information that should not appear in the public directory.

## Markdown

The About editor supports CommonMark headings, emphasis, lists, links, block
quotes, code, and horizontal rules. Raw HTML is displayed as text.

Images embedded with Markdown are not rendered on saved listings. Image nodes
are reduced to their alternative text so a listing cannot make visitors load
content from an untrusted image host. Use a normal link for screenshots and
diagrams.

## Manage a listing

Your dashboard lists projects owned by the current account. Ownership comes
from the authenticated session and cannot be selected in the form. Only the
owner may update or delete a listing.

For request and response details, see the
[HTTP API reference](../reference/api.md#create-a-project).
