# TRACE hosting and interview launch

The deployment architecture for the current implementation is **Vercel Hobby for the Next.js frontend + a Linux VM for the Python backend and private Ollama sidecar**. The interview deployment uses a Google Cloud trial-funded Compute Engine VM; Oracle remains an alternative for later permanent free hosting. Cloudflare Workers AI supplies hosted text/code/images; OCR, extraction, retrieval and speech run on the VM. Visitors enter no provider key. The owner configures Cloudflare once, privately on the backend. Optional visitor OpenAI mode remains separate. The private Hugging Face ZeroGPU image-only fallback is enabled after explicit Cloudflare capacity rejection. Its [setup and acceptance status](huggingface-images.md) records successful live inference and the remaining public-browser quota check.

As of 9 October 2026, the production website is **https://trace-agentic-workspace.vercel.app**, backed by **https://trace-api.34.93.169.35.sslip.io**. It is accessible without a Vercel login or visitor API key. Real browser Turnstile entry, speech playback, local summary fallback and five labeled samples were verified. The site is live; full output-quality/interview acceptance is still incomplete. See [the launch record](launch-2026-10-09.md) for the distinction.

The dedicated Google Compute Engine host is `trace-api`, zone `asia-south1-a`, `n2-standard-4` (4 vCPU/16 GB), Ubuntu 24.04 AMD64, 50 GB disk. Mumbai E2 quota was zero. Its reserved address is `trace-api-ip`; the host has no attached service account. Only HTTP/HTTPS are public; SSH is restricted to the owner's setup IP. Caddy terminates HTTPS; API/Ollama ports remain private. Backend source is detached at **3529b105ffee12b5b90858f8d625f2cde19e8b05**. Vercel deployment `dpl_F5FMTnrKFjsTapNzd2UroSWL6stA` adds the external-provider disclosure; the approved frontend design is unchanged.

The account remains **Free Trial**, with an observed expiry of **8 January 2027**, or earlier credit exhaustion. Do not upgrade it. Compute, disk and network consume trial credits; this is temporary zero-cash hosting, not an indefinitely free 16 GB VM. Check the actual remaining credit in Billing. The trial expiry is not an uptime promise. [Google trial rules](https://cloud.google.com/signup-faqs).

## What Vercel alone would do

| Deployment | Working behavior | Missing behavior |
| --- | --- | --- |
| Frontend only | Landing page, all tool forms/navigation, five labeled offline samples, local voice previews, themes and in-tab drafts | Every live workflow calls the Python API. Without its public HTTPS URL, generation, uploads, OCR, speech, indexing, Q&A, source extraction, verification and advanced OpenAI execution fail. An OpenAI key does not replace the backend. |
| Frontend + tested VM API | All fifteen tool integrations have their required runtime and storage | Provider quotas, source-site restrictions and CPU latency still apply. No guarantee of universal factual accuracy or unlimited usage. |
| Move this backend into Vercel functions unchanged | Not a supported migration of this application | Persistent SQLite/files/FAISS, shared quota counters, model caches, long CPU workflows and the private Ollama sidecar cannot be assumed to survive stateless function scaling. |

Vercel currently supports Python and OCI container functions. This is not a claim that Vercel cannot host any backend. Its Hobby function limits are 2 GB/1 vCPU and 300 seconds with Fluid Compute, with a 4.5 MB request/response payload limit. Standard Python bundles allow 500 MB; large-function beta raises package size to 5 GB but does not solve memory, duration or durable storage. TRACE permits 200 MB file uploads and has a 900-second workflow deadline; its VM composition budgets 3 GB for the API and 8 GB for Ollama. Earlier local research cases took 293–492 seconds on two CPU threads. The browser must upload and receive workflow events **directly from the VM**, rather than through a Vercel API proxy.

Sources: [Vercel function limits](https://vercel.com/docs/functions/limitations), [Python runtime](https://vercel.com/docs/functions/runtimes/python), [container deployments and statelessness](https://vercel.com/kb/guide/does-vercel-support-docker-deployments). Vercel Hobby is intended for personal noncommercial use; this personal portfolio is the proposed use. [Hobby plan](https://vercel.com/docs/plans/hobby).

## Alternative only: Oracle account and VM

1. Open [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) and complete account/email/phone/card verification yourself. Keep the account free; do not select paid shapes or upgrade to bypass capacity problems.
2. Choose a home region carefully. Always Free compute is restricted to that region. Capacity is not guaranteed. If unavailable, try another availability domain in that home region where offered, or report the capacity message so we can reassess the interview timeline.
3. Create a dedicated compartment and an **Always Free eligible `VM.Standard.A1.Flex` Ubuntu instance: 2 OCPUs, 12 GB RAM, 50 GB boot volume**. Check any other account resources before allocating: current account-wide A1 free allocation is equivalent to 2 OCPUs/12 GB, with 200 GB combined boot/block storage.
4. Save the SSH private key on your computer. Provide only the public IP, SSH username (usually `ubuntu`) and local key-file path to continue setup. Never paste the private key or provider token into chat.
5. Restrict TCP 22 to your own public IP. Allow public TCP 80/443 in the Oracle security list/NSG and the Ubuntu firewall. Keep 8000 and 11434 private.
6. Create a DNS hostname pointing to the VM, using an existing domain or [DuckDNS](https://www.duckdns.org/). Prefer a direct DNS record for the API while testing long responses, rather than inserting another untested proxy.

Oracle may reclaim idle free VMs; they are not an uptime guarantee. Capacity/reclamation make early provisioning and a reconstruction procedure important for an interview. [Current Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm), [launching an instance](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm).

## Backend installation after access is available

Install Docker Engine/Compose using the [official Ubuntu instructions](https://docs.docker.com/engine/install/ubuntu/) and Caddy using its [official package instructions](https://caddyserver.com/docs/install). Clone the repository and check out the reviewed `codex/trace-react-workspace` commit. Keep the deployed commit recorded; moving production to a later commit is an explicit release.

Copy `backend/.env.example` to ignored `backend/.env`, protect it with mode 600, and enter values directly in the file. No credentials are baked into Docker images. Configure:

| Backend variable | Production value |
| --- | --- |
| `TRACE_CLOUDFLARE_ACCOUNT_ID` / `TRACE_CLOUDFLARE_API_TOKEN` | Existing owner Workers AI account/token |
| `TRACE_PUBLIC_DEPLOYMENT` | `true` |
| `TRACE_ALLOWED_ORIGINS` | Exact HTTPS Vercel origin(s), comma-separated; no wildcard |
| `TRACE_TURNSTILE_SECRET` | Secret from the real Turnstile widget |
| `TRACE_TURNSTILE_HOSTNAMES` | Exact frontend hostname(s), without scheme/path |
| `TRACE_IP_HASH_SECRET` | A stable random secret generated locally and entered privately |
| `TRACE_TRUSTED_PROXY_IPS` | Exact reverse-proxy peer IP as seen inside the API container |

Bring up the existing composition, warm every required pinned asset, then verify native compilers:

```sh
docker compose up -d --build
docker compose --profile setup run --rm --build model-setup
docker compose exec backend python -m backend.warmup
docker compose exec -e TRACE_PUBLIC_DEPLOYMENT=false -e TRACE_REQUIRE_COMPILER_ISOLATION=1 backend python -m pytest backend/tests -q -p no:cacheprovider
```

The test-only environment override above applies to the separate test process: TestClient fixtures create sessions without a real browser proof. Never turn off public protection in the running API or production environment. Real missing-proof rejection and successful browser entry must be verified separately.

`compose.yaml` keeps API port 8000 bound to host loopback; Ollama has no public port. Named volumes persist SQLite/session data, indexes, artifacts and models. Keep one API process. Do not delete volumes during updates; `docker compose down -v` deletes that data. Retention remains at most 24 hours for session data. Warm model files remain cached separately.

Host-installed Caddy configuration (`/etc/caddy/Caddyfile`, replace the hostname):

```caddyfile
trace-api.your-domain.example {
    reverse_proxy 127.0.0.1:8000 {
        header_up X-Forwarded-For {remote_host}
        flush_interval -1
    }
}
```

This direct-to-Caddy setup overwrites visitor forwarding headers. The API container may see Docker's bridge gateway as the peer, rather than host loopback. Determine the actual peer before setting `TRACE_TRUSTED_PROXY_IPS`; do not trust arbitrary addresses or all private ranges. Validate and reload Caddy, then confirm HTTPS and streaming. [Caddy proxy headers/streaming](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy), [automatic HTTPS](https://caddyserver.com/docs/automatic-https).

The current 16 GB VM leaves roughly 5 GB outside the 3 GB API/8 GB Ollama ceilings. Active-model samples are recorded in the launch evidence; they are not a two-workflow peak stress certification. Measure **combined actual peak memory**, CPU contention and latency before claiming concurrent capacity. Local Mac timings do not establish target-server performance.

## Vercel frontend and Turnstile

1. Sign in to Vercel with GitHub and import `Archit-k20/Agentic-Workflows-GenAI-`. Use **Root Directory `frontend`**, the detected Next.js preset, its default build and lockfile. Deploy the reviewed migration branch for validation without merging unfinished work into main.
2. Establish the intended `*.vercel.app` hostname. A custom website domain is optional. Use a preview while setup is incomplete; do not distribute a frontend-only link as a functioning app.
3. In Cloudflare, create a free **Turnstile** widget for that exact frontend hostname. Save its secret only in the backend and its public site key in Vercel. Add any specific preview hostname deliberately to widget/backend allowlists; no blanket wildcard.
4. Configure Vercel environment variables for the deployment environment being tested:
   - `NEXT_PUBLIC_API_URL=https://your-api-hostname` (no `/api/v1`, no trailing slash, never localhost).
   - `NEXT_PUBLIC_TURNSTILE_SITE_KEY=your-public-site-key`.
5. Rebuild/redeploy after changing either value: `NEXT_PUBLIC_` values are bundled at build time. No Cloudflare token, Turnstile secret or OpenAI key belongs in frontend variables.
6. Restart the backend after setting the exact matching origin/Turnstile hostname and secret. Perform public checks before production promotion. Ensure the eventual recruiter URL does not require a Vercel account or preview-password login.

[Turnstile setup](https://developers.cloudflare.com/turnstile/get-started/), [server validation](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/).

Run the no-inference public check from the prepared backend container:

```sh
docker compose exec backend python -m backend.deployment_check \
  --frontend-origin https://your-project.vercel.app \
  --api-origin https://your-api-hostname
```

It checks HTTPS API wiring, installed capabilities, exact CORS, free default mode, public protection and rejection of missing visitor proof. It sends no AI request or credentials. A pass does not establish successful browser Turnstile, generation quality, persistent storage, memory or latency.

## Operating the deployed host

Use the authenticated `trace-interview` gcloud configuration and the owner account. The CLI installed for this launch is `/tmp/trace-tooling/google-cloud-sdk/bin/gcloud`; this temporary installation may need reinstalling after OS cleanup. Credentials are in Google's normal user configuration, not in Git. Example:

```sh
/tmp/trace-tooling/google-cloud-sdk/bin/gcloud --configuration=trace-interview \
  compute ssh trace-api --zone=asia-south1-a \
  --project=project-bcfdd038-efca-4fec-bb9
```

On the host, source is `/opt/trace/app`; private owner configuration is `/opt/trace/app/backend/.env`, root-owned mode 600. Caddy uses `/etc/caddy/Caddyfile`. The upstream Caddy package repository returned HTTP 402 during setup; Ubuntu's Caddy package was used successfully. `TRACE_TRUSTED_PROXY_IPS=172.18.0.1` matches the measured Docker peer for this network; remeasure after network reconstruction.

```sh
cd /opt/trace/app
sudo docker compose ps
sudo docker stats --no-stream
sudo systemctl status caddy --no-pager
sudo docker compose logs --tail 100 backend
```

Do not publish logs containing visitor inputs. To update deliberately: record the old commit, fetch and check out the reviewed release commit, then `sudo docker compose up -d --build backend`. Re-run health/public wiring and one controlled browser check. To roll back, check out the recorded old commit and rebuild the backend, retaining named volumes. Do not use `down -v`. Storage-format migrations would need a separate backup/rollback review; none is proposed here.

An ignored local `backend/.env.production` recovery copy (mode 600) retains the stable private production configuration. Back up it and named data volumes securely if reconstruction is needed; never commit credentials or visitor data. Only temporary synthetic launch-test sessions were cleared, not live visitor sessions. Anonymous data expires within 24 hours. The immutable model installer rebuilds the model cache without relying on a changed registry tag.

The reserved IP keeps the current API hostname stable. If the VM is rebuilt with another address, update API hostname, HTTPS and the frontend build-time API URL. If the owner's IP changes, update only the dedicated SSH rule to the new owner IP/32; do not open SSH globally. Monitor Billing credit/expiry and disk space before the interview. At trial end, move to a verified free alternative or stop/delete the dedicated VM, disk and reserved IP rather than upgrading to paid billing. Stopping a VM alone is not a permanent cleanup of its disk/IP resources.

Vercel production was deployed through its official CLI from `frontend`; GitHub auto-deployment was not enabled, and this draft branch was not merged. The public project has Vercel authentication protection disabled so recruiters can open it. Rebuild production deliberately after changing frontend source or `NEXT_PUBLIC_` values. Preview URLs need explicit backend/Turnstile allowlisting before live execution.

## Interview release acceptance

- Finish the seven hosted boundaries, affected cases and complete sixty-case source-based review on one recorded inference profile. Pause honestly at allowance limits and resume only deliberately; do not reset/bypass the ledger.
- Exercise actual article URLs and available/pasted transcripts; blocked source sites retain a readable recovery path. Test real PDF/DOCX and scanned image input. Listen to speech and inspect one generated image.
- In the public browser, prove Turnstile success, all fifteen forms/live integrations, event stages, failed/partial outputs, long uploads, audio/image delivery, session isolation/clear and Q&A restart recovery.
- Measure target-VM memory and latency for hosted operation and CPU fallback. Long fallback responses must remain explicitly identified. Review source accuracy; compiler checks only prove syntax/compilation.
- Verify the approved mobile/desktop interface and deployed frontend performance. Keep labeled samples available but never substitute them for a failed live request.
- Review the PR/checks, record the release commit, promote the tested production URL, and check it from another device/network with no account/key. Only then share it with recruiters.
- Avoid spending the shared inference allowance on a full benchmark immediately before the interview. Confirm available capacity with one short deliberate smoke check; do not fabricate a reserved quota or promise unlimited use. Have a reconstruction/rollback procedure and a clearly labeled sample walkthrough if a provider becomes unavailable.

## Strictly free alternatives: checked 8 October 2026

The owner requires **zero hosting spend**. Among the services checked, there is no established equivalent indefinitely free VM that we have verified for this unchanged 11 GB container composition. Vercel remains the frontend in every option. Trial credits can cover an interview deployment, but they are not permanent free hosting.

| Zero-cost route | Eligibility and duration | Full-backend fit / remaining work |
| --- | --- | --- |
| Google Cloud Free Trial + Compute Engine VM | Eligible new customers: USD 300 credit for up to 90 days or credit exhaustion. No usage charges while the account stays in the trial; do not manually upgrade. Identity/payment verification can be required. | A trial-covered Ubuntu VM with about 16 GB RAM can run the existing composition, subject to account quota/capacity and actual credit cost. Service stops when the trial ends. This uses Compute Engine, not the separate Cloud Run storage migration. Best interview candidate **if temporary hosting is acceptable and the owner is eligible**. |
| AWS Free account plan + EC2 | Eligible new customers: USD 100 immediately, up to USD 200 earned total, at most six months or credit exhaustion. Stay on the Free account plan; do not activate paid-only services. | Credits are temporary. Available free-plan instance types are restricted; eligible large instances listed are not a confirmed single 16 GB host. Full API/private model deployment needs supported capacity/architecture checks rather than promising a one-click unchanged deployment. |
| Azure for Students | Verified eligible higher-education student: USD 100 credit, no credit card required. | A suitably sized VM consumes credits quickly; quota/region availability and eligibility need verification. This is a credit-funded option, not unlimited 16 GB free compute. |
| Existing computer + Tailscale Funnel | Funnel is available on all plans; personal free account eligibility applies. Public HTTPS URL is reachable without visitor Tailscale accounts. | No rented-server fee, but the machine, Docker/backend and internet must remain on. Funnel has bandwidth limits; long workflow events/uploads, public protection and trusted proxy identity need actual verification. Backup for a scheduled demonstration, not an independent always-on cloud deployment. |

[Google trial rules and no automatic upgrade](https://cloud.google.com/signup-faqs), [Google free-program details](https://docs.cloud.google.com/free/docs/free-cloud-features), [AWS Free plan](https://aws.amazon.com/free/), [eligible EC2 types](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html), [Azure for Students](https://learn.microsoft.com/en-us/azure/education-hub/about-azure-for-students), [Tailscale Funnel](https://tailscale.com/docs/features/tailscale-funnel).

Historical signup guidance (completed for this launch): open Google Cloud Free Trial, personally complete verification, confirm the Billing overview says **Free trial**, create a dedicated project, enable Compute Engine, and check the displayed estimate/credit balance and VM quota before creating a roughly 16 GB Ubuntu VM. Restrict SSH to the owner IP and expose only HTTPS/HTTP publicly. Record the trial end/remaining credit and do not upgrade to paid billing. Then use the VM/backend/Turnstile/Vercel checks in this guide. The owner completed signup and authentication; the dedicated VM above has now been provisioned and tested.

Google's ongoing e2-micro allowance is about 1 GB RAM, so it cannot keep this full runtime after trial expiry. Render Free has no persistent disk and insufficient resources. New personal Hugging Face Docker Spaces require PRO; its free-account ZeroGPU Gradio exception is not a drop-in Docker backend. Cloudflare Quick Tunnels explicitly do not support SSE, so they are unsuitable for TRACE's workflow event transport. [Google machine types](https://docs.cloud.google.com/compute/docs/general-purpose-machines), [Render free restrictions](https://render.com/docs/free), [Spaces requirements](https://huggingface.co/docs/hub/spaces-overview), [Quick Tunnel limits](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).

## Paid comparison retained for reference; excluded by owner preference

For the one-week interview timeline, a **16 GB Ubuntu VPS + Vercel frontend** is the smallest architectural change. The current container ceilings total 11 GB; leave room for the OS and proxy and measure combined real peak usage before accepting capacity. Prices below are provider examples, not a purchased configuration or measured monthly bill. Taxes, IPv4, storage and other extras can apply. Server availability and account approval must be checked at signup.

| Alternative | Current pricing / constraint | Fit for TRACE |
| --- | --- | --- |
| Hetzner cost-optimized VPS | EU CX43: 16 GB, 8 vCPU, 160 GB; EUR 15.99/month excluding VAT/IPv4. ARM CAX31: 16 GB, EUR 20.99/month excluding VAT/IPv4. The provider lists limited capacity, with unavailable locations in the public catalog. | Best budget candidate **if available**; CPU is shared/variable. Run the existing composition, then test native architecture, latency and peak RAM. |
| DigitalOcean Basic Droplet | Regular 16 GiB/8 vCPU/320 GiB: USD 96/month. Per-second compute billing with monthly cap; optional backups/add-ons extra. | Straightforward VPS alternative with the same deployment approach. The USD 4–6 plans do not fit this runtime. |
| Railway | Hobby USD 5 minimum credits usage; container RAM USD 10/GB/month, CPU USD 20/vCPU/month, storage/egress extra. Actual usage is billed. | More managed deployment, but not a flat USD 5 solution. API/private Ollama volumes, isolation and long requests need validation. Estimate actual usage before choosing. |
| Render | Free service: 512 MB, sleeps, no persistent disks. Paid larger instances and disks are required. | Paid managed hosting is possible; cannot run this whole backend on its free tier. Service/private model packaging and cost need selection/testing. |
| Google Cloud Run | Free allowances exist, but billing is required and ancillary services can cost money. Writable container storage is ephemeral. | Requires durable/shared storage and coordination instead of current SQLite/local files. Additional migration/testing makes it a weaker choice for this deadline. |
| Hugging Face Spaces | Current new personal Docker/Gradio Space creation requires PRO; CPU Basic is 16 GB/2 vCPU with 50 GB temporary disk, and free hardware sleeps. Free-account ZeroGPU Gradio exceptions do not directly host this Docker backend. | Useful ML demo environment, but not an always-on, permanently free Docker replacement. Ephemeral storage violates restart persistence without further work. |

Sources: [Hetzner specifications/capacity](https://www.hetzner.com/cloud/cost-optimized/), [current Hetzner prices](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/), [DigitalOcean pricing](https://www.digitalocean.com/pricing/droplets), [Railway plans and metering](https://docs.railway.com/pricing/plans), [Render free limitations](https://render.com/docs/free), [Cloud Run pricing](https://cloud.google.com/run/pricing), [Cloud Run container storage](https://docs.cloud.google.com/run/docs/container-contract), [Spaces overview](https://huggingface.co/docs/hub/spaces-overview).

Google Free Trial Compute Engine is selected for the interview deployment. No paid plan, account upgrade or hosting purchase was made; the paid comparisons above remain excluded by the owner's zero-spend preference. Paying for a server does **not** raise Cloudflare's inference allowance; samples and explicitly identified local fallback remain separate experiences, and the CPU fallback still needs quality/capacity acceptance. Do not rush a Vercel-only/backend rewrite while implying unchanged feature parity.

Original Streamlit remains available locally using `requirements.txt` and `streamlit run main.py`. Original OpenAI advanced mode is optional and has no paid live acceptance evidence without an explicitly supplied test key. No paid provider is required for default visitor access.
