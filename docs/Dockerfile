FROM python:3.13-slim AS builder

WORKDIR /docs

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdocs build --strict


FROM nginx:alpine AS runtime

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /docs/site /usr/share/nginx/html

ENV PORT=8080

EXPOSE 8080
