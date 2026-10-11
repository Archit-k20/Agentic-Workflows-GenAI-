# Deployment and operations

TRACE uses **Vercel for the Next.js frontend and Google Compute Engine for the FastAPI backend**, with a private Ollama service and Caddy HTTPS proxy. The single visitor entry link is at the top of the [project README](../README.md). Do not distribute individual preview deployments as alternate application links.

Cloudflare provides hosted text, code and images. The optional private Hugging Face worker supplies image fallback after an explicit capacity rejection. Extraction, OCR, retrieval, local text and free speech run on the VM. See [architecture](architecture.md), [provider configuration](free-access.md) and [image fallback](huggingface-images.md).

## Current hosting

| Component | Configuration |
| --- | --- |
| Frontend | Vercel project `trace-agentic-workspace`, project root `frontend`, Next.js build |
| Backend | Google project `project-bcfdd038-efca-4fec-bb9`, instance `trace-api`, zone `asia-south1-a` |
| VM | Ubuntu 24.04 AMD64, `n2-standard-4`, 4 vCPU, 16 GB RAM, 50 GB disk |
| API origin | `https://trace-api.34.93.169.35.sslip.io` |
| Runtime | Docker Compose; API: 2 CPUs/3 GB, Ollama: 2 CPUs/8 GB; one API worker |
| Network | Caddy exposes HTTPS; API binds host loopback; Ollama has no public port; SSH is restricted to the owner's IP |
| Storage | Mounted private volumes for temporary session data, SQLite, indexes and model assets |

The VM uses **Google trial credits**. The last account inspection showed a trial expiry of 8 January 2027, or earlier credit depletion. This is not indefinitely free hosting or an uptime commitment. Check the owner's Billing dashboard for the actual current balance. No paid upgrade is part of this project setup. [Google trial rules](https://cloud.google.com/signup-faqs).

## Why the complete app needs a backend

A Vercel-only deployment supports the introduction, collection, navigation, forms, five offline examples and bundled voice previews. All live workflows require the Python API, including advanced OpenAI mode. The backend relies on persistent files, native compilers/OCR, local model assets, shared usage counters and requests lasting up to 900 seconds. It cannot be moved unchanged to stateless frontend functions.

Uploads and workflow events go directly from the browser to the HTTPS API. Do not introduce a frontend proxy that imposes smaller upload or execution limits. A future serverless backend would need a separate storage, concurrency and model-runtime design.

## Reproduce the backend

Install Docker Engine with Compose and Caddy from their official distributions. Clone this repository and check out the reviewed release commit; record that commit for rollback. The deployed checkout is `/opt/trace/app`.

Copy `backend/.env.example` to ignored `backend/.env` if the file does not exist. Protect it with mode 600 and enter owner credentials privately. Do not overwrite existing production configuration.

| Variable | Purpose |
| --- | --- |
| `TRACE_CLOUDFLARE_ACCOUNT_ID`, `TRACE_CLOUDFLARE_API_TOKEN` | Owner Workers AI access; retain the Free plan boundary |
| `TRACE_PUBLIC_DEPLOYMENT` | Set to `true` for public hosting |
| `TRACE_ALLOWED_ORIGINS` | Exact HTTPS frontend origins, comma-separated; no wildcard |
| `TRACE_TURNSTILE_SECRET`, `TRACE_TURNSTILE_HOSTNAMES` | Real widget secret and exact permitted hostnames |
| `TRACE_IP_HASH_SECRET` | Stable private value for persistent network fair-use accounting |
| `TRACE_TRUSTED_PROXY_IPS` | Actual reverse-proxy peer addresses as seen by the API container |
| `TRACE_HF_SPACE_ID`, `TRACE_HF_API_TOKEN` | Optional private image worker and read-only runtime credential |

Run from the repository root:

```sh
docker compose up -d --build
docker compose --profile setup run --rm --build model-setup
docker compose exec backend python -m backend.warmup
```

The installer verifies immutable model blobs. Do not replace it with a mutable model tag. Keep one API process so the shared CPU gate and two workflow slots retain their intended behavior. Named volumes survive container restarts; `docker compose down -v` would delete them. Session data expires within 24 hours; model caches are separate.

Caddy configuration, substituting your API hostname:

```caddyfile
trace-api.your-domain.example {
    reverse_proxy 127.0.0.1:8000 {
        header_up X-Forwarded-For {remote_host}
        flush_interval -1
    }
}
```

The proxy overwrites untrusted forwarded addresses. The current Docker network previously exposed peer `172.18.0.1`; measure again after network reconstruction instead of trusting an entire private range. Keep ports 8000 and 11434 private. [Caddy streaming and headers](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy).

## Release the frontend

1. Use the existing Vercel project with root directory `frontend`, Node.js 24, the committed lockfile and the Next.js preset.
2. Set `NEXT_PUBLIC_API_URL` to the HTTPS API origin without `/api/v1` or a trailing slash. Set `NEXT_PUBLIC_TURNSTILE_SITE_KEY` to the widget's public site key. These values are bundled at build time, so changing them requires a new build.
3. Keep provider tokens, visitor OpenAI keys and the Turnstile secret out of frontend environment variables and source files.
4. Build and inspect a preview. Live requests from a preview require its exact origin and hostname in both backend and widget allowlists. Offline examples do not.
5. Promote the reviewed interface to the existing production alias. The README continues to use that one stable destination. Keep the preceding deployment available for rollback.
6. Check the public introduction, collection, direct tool routes, settings and examples after promotion. Production must remain accessible without a Vercel login.

Production releases have been made with the official Vercel CLI. A Git push alone should not be treated as evidence that production changed: check the deployment and alias after every release. [Turnstile setup](https://developers.cloudflare.com/turnstile/get-started/), [server validation](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/).

## Checks and recovery

Run the public wiring check from the prepared backend container, replacing the two origins with your configured values:

```sh
python -m backend.deployment_check \
  --frontend-origin https://your-frontend.example \
  --api-origin https://your-api.example
```

It checks HTTPS configuration, capabilities, CORS and rejection of missing visitor proof without making an AI request. It does not prove successful generation or model quality. Current verification scopes and pending checks are in [verification](verification.md).

For the existing host, use the owner's authenticated gcloud CLI:

```sh
gcloud --configuration=trace-interview compute ssh trace-api \
  --zone=asia-south1-a --project=project-bcfdd038-efca-4fec-bb9
```

On the host:

```sh
cd /opt/trace/app
sudo docker compose ps
sudo docker stats --no-stream
sudo systemctl status caddy --no-pager
```

Record the old commit before an update. Fetch and check out the reviewed release, then rebuild only the required service with `sudo docker compose up -d --build backend`. Run health and wiring checks afterward. Roll back by rebuilding the recorded preceding commit while retaining volumes. Storage-format changes would require a separate backup/migration review.

Keep owner environment files and any recovery copies private; never commit credentials or visitor data. Monitor combined memory, disk space, provider capacity and trial credit. Memory samples are not peak-load certification. If the API IP changes, update its hostname, certificate and frontend build-time configuration. At trial end, arrange replacement hosting or remove the dedicated resources; merely stopping a VM does not remove its disk or reserved IP.
