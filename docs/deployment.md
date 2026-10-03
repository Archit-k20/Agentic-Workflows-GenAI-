# Deployment preparation — no services have been provisioned

## Local verification

From the repository root:

```sh
docker compose up --build -d
npm ci --prefix frontend
npm --prefix frontend run dev
```

Open http://localhost:3000. Backend health is http://localhost:8000/api/v1/health. The first local summary downloads and loads `sshleifer/distilbart-cnn-12-6`; the model cache volume is reused. No API key is needed for local summarization/OCR or any bundled sample. Live generator/assistant workflows require your own key in Settings. Original Streamlit remains available using `requirements.txt` and `streamlit run main.py`.

```sh
npm --prefix frontend run typecheck
npm --prefix frontend test
npm --prefix frontend run build
docker compose run --rm backend python -m pytest backend/tests -q -p no:cacheprovider
```

To regenerate contracts:

```sh
docker compose run --rm backend python -c 'import json; from backend.app import app; print(json.dumps(app.openapi(), indent=2))' > backend/openapi.json
npm --prefix frontend run generate:types
```

Build a single architecture explicitly with `docker build --platform linux/arm64 -f backend/Dockerfile -t trace-backend:arm64 .` (or linux/amd64). Native Linux is required to verify compiler isolation; cross-architecture emulation reports it unavailable. CI uses native x86 and ARM runners.

## Vercel frontend (later)

Import this GitHub repository into Vercel Hobby, set **Root Directory** to `frontend`, and use its default Next.js build. Set `NEXT_PUBLIC_API_URL` to the backend HTTPS origin, without `/api/v1` or a trailing slash. This URL is public configuration, never a secret. No OpenAI key belongs in Vercel environment variables or the build. Validate a preview before production promotion. Because the browser uploads directly to Python, uploads and long-running event responses do not go through frontend functions.

## Provisional Oracle backend (later)

1. Complete your own Oracle Free Tier identity verification. Most users need a phone/card. Choose the home region carefully; free capacity may be unavailable. Do not choose a paid shape to bypass capacity limits.
2. Create a dedicated compartment and an Always Free Ampere A1 Ubuntu VM, provisionally **2 OCPUs / 12 GB RAM / 50 GB boot storage**, within the account-wide free allocation. Restrict SSH to your IP and open HTTP/HTTPS only.
3. Install Docker, copy/clone the tested release, and build ARM64. Keep port 8000 bound to loopback; mount private data/model volumes; enable restart-on-failure.
4. Supply a hostname (existing domain or DuckDNS). Use Caddy to proxy the HTTPS hostname to `127.0.0.1:8000`. Its automatic certificates require working DNS and public ports 80/443.
5. Set `TRACE_ALLOWED_ORIGINS` to the exact Vercel production origin and each approved preview origin, comma separated. No wildcard origins. Restart the backend after changes. Do not store user API keys in its environment.
6. Check HTTPS uploads, event delivery, Q&A processing/querying, media ownership, clearing, and restart recovery before promoting the frontend.
7. Monitor memory/disk and free-instance eligibility. Keep reconstruction/configuration documented: Oracle may reclaim idle free instances. Do not back up temporary user documents as permanent history.

Example Caddyfile (replace the hostname):

```caddyfile
trace-api.your-domain.example {
    reverse_proxy 127.0.0.1:8000 {
        flush_interval -1
    }
}
```

`TRACE_DATA_DIR` defaults to `/data` in the image, `HF_HOME` to `/model-cache`. The Docker image runs as UID 10001; bind mounts must be writable by this UID and private. Only the HTTPS proxy should be publicly reachable. Cloud provisioning/publishing has not been performed.

Official references: [Oracle Free Tier](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm), [Always Free allocations and reclamation](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm), [launching an instance](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm), [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https), [DuckDNS](https://www.duckdns.org/).

## Cloud Run alternative (later)

Google Cloud Console is the management interface; Cloud Run is the container service. It requires billing. Free allowances may cover a small workload, but build/image storage, transfer, and excess usage can incur charges. Budget alerts are not spending caps. Trial credits expire. A switch requires a shared storage adapter, durable metadata, and concurrency limits across replicas.

Later sequence: project/billing → enable Cloud Run, Artifact Registry and Cloud Build → build/push → configure shared storage and deployment settings → zero minimum instances with bounded scaling → HTTPS endpoint → Vercel origin configuration → end-to-end verification. [Free program](https://docs.cloud.google.com/free/docs/free-cloud-features), [pricing](https://cloud.google.com/run/pricing), [Python deployment guide](https://docs.cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service).

Existing OpenAI usage is separately metered. Local samples make no provider requests.
