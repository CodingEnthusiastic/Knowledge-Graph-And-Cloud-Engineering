# Question 2 — Part B: Cloud Migration & Scaling Plan

**Target Application:** Production AI Case-Management App (Llama 3.1 8B, PostgreSQL, FastAPI, Caddy)  
**Target Scale:** 200 Active Users (~1,000 questions/day)  
**Budget Constraint:** ₹25,000 INR per month (~$300 USD)  
**Author:** Cloud & Infrastructure Engineering Candidate  
**Date:** October 2026 (Max 1.5 Pages)

---

## 1. Hosting Architecture Comparison & Selection

| Strategy | Architecture Overview | Pros | Cons | Monthly Cost (INR) | Verdict |
|---|---|---|---|---|---|
| **Option A: Pure On-Premises Office Server** | Keep all 5 components on the office Ubuntu machine; add UPS power and dual broadband. | Zero cloud compute fees; uses existing 24GB GPU. | Subject to power cuts, physical theft, ISP routing drops, and router misconfigurations (Part A). | ~₹4,500 (Electricity + 2nd ISP) | **REJECTED:** Inadequate SLA and high security liability for private case notes. |
| **Option B: Pure Cloud (Full Dedicated GPU Instance)** | Rent a full-time cloud GPU VPS (e.g., RunPod / Lambda RTX 4090 24GB 24/7). | Single host, high bandwidth, standard cloud uptime. | Dedicated 24/7 GPU costs $0.44/hr $\times$ 730h = $321 (~₹27,000/mo), exceeding budget once storage and egress are added. | ~₹27,000–₹32,000 | **REJECTED:** Exceeds the ₹25,000/mo hard budget cap. |
| **Option C (RECOMMENDED): Cloud Core + Serverless/Private GPU Tier** | Host Web, API, Postgres, Worker, and Caddy on a reliable **Hetzner Cloud VPS** (Europe/Falkenstein or Ashburn) with automated backups. Route AI inference to **RunPod Serverless GPU (RTX 4090/A4000 24GB)** paying only per second of inference, OR connect to office GPU via zero-trust **Tailscale Mesh VPN**. | High 99.99% availability for patient notes; zero public ports on office router; cost scales strictly with usage; fits well inside budget. | Requires secure API key management between VPS and GPU inference worker. | **~₹7,200 / month** (Leaves ₹17,800 buffer) | **SELECTED:** Maximum reliability, top security, and lowest cost. |

**Why Option C is Chosen:** Sensitive case notes, web frontend, and database remain in a hardened, ISO-27001 certified cloud data center with automated daily snapshots. The GPU inference runs either via per-second serverless GPU endpoints or over an outbound-only Tailscale tunnel, eliminating router port-forwarding issues forever.

---

## 2. GPU Calculations (VRAM & Concurrency Capacity)

### (a) VRAM Footprint for Llama 3.1 8B Model
- **Parameters ($N$):** $8.03 \times 10^9$ parameters.
- **16-bit Form (FP16 / BF16):**
  - Weights: $8.03 \times 2 \text{ bytes} \approx 16.06\text{ GB}$.
  - KV Cache & Activations (for 4k context): $\approx 3.0\text{ GB}$.
  - CUDA runtime overhead: $\approx 1.5\text{ GB}$.
  - **Total VRAM needed (16-bit):** **$\approx 20.5\text{ GB}$**.  
  - *Fit in 24 GB?* **Yes**, it fits in a 24 GB card (RTX 3090/4090/A10G), but leaves limited headroom for concurrent request batching.
- **4-bit Form (AWQ / GPTQ / GGUF Q4_K_M):**
  - Weights: $8.03 \times 0.5 \text{ bytes} \approx 4.02\text{ GB}$.
  - KV Cache & Activations: $\approx 2.0\text{ GB}$.
  - CUDA runtime: $\approx 1.2\text{ GB}$.
  - **Total VRAM needed (4-bit):** **$\approx 7.2\text{ GB}$**.  
  - *Fit in 24 GB?* **Yes, with 16.8 GB of free headroom!** This surplus VRAM allows massive PagedAttention KV-cache allocation, supporting 20+ concurrent active streams without performance degradation.

---

### (b) Traffic Load & Concurrency Peak Analysis
- **Daily Volume:** 200 users $\times$ 5 questions/day = **1,000 queries/day**.
- **Peak Window (10:00 AM – 6:00 PM = 8 hours = 28,800 seconds):**
  - Peak queries: $80\% \times 1,000 = \mathbf{800\text{ queries}}$.
  - Compute demand: $800 \times 10\text{ seconds} = \mathbf{8,000\text{ GPU-seconds}}$.
  - **Duty Cycle:** $\frac{8,000\text{ s}}{28,800\text{ s}} = \mathbf{27.78\%}$ (The GPU is idle $\approx 72\%$ of the working day).
  - Average arrival rate: 1 query every $\frac{28,800}{800} = \mathbf{36\text{ seconds}}$.
- **Is 1 GPU enough?**
  - **Yes.** On average, 1 GPU easily handles this workload since queries arrive every 36 seconds on average while taking only 10 seconds to generate.
- **What happens if 10 users ask a question at the exact same moment?**
  - *Under naive single-threaded queuing:* Requests queue sequentially; user 1 waits 10s, but user 10 waits $10 \times 10 = \mathbf{100\text{ seconds}}$ (unacceptable latency).
  - *Under production continuous batching (vLLM / TGI with PagedAttention):* In 4-bit mode (7.2 GB weights), vLLM batches all 10 requests concurrently across the tensor cores. Total execution time for all 10 requests is $\approx 16–20\text{ seconds}$ total.
  - *Streaming User Experience:* Users receive tokens immediately via Server-Sent Events (SSE), keeping Time-To-First-Token (TTFT) under **1.8 seconds**, preventing timeouts and keeping perceived latency low.

---

## 3. Monthly Cost Breakdown (Within ₹25,000 Budget)

| Infrastructure Item | Specifications & Provider | Monthly Price (USD) | Monthly Price (INR) | Source URL | Verification Date |
|---|---|---|---|---|---|
| **App & DB Cloud Server** | **Hetzner Cloud CPX31** (4 vCPU AMD, 8 GB RAM, 160 GB NVMe, 20 TB Traffic, Static IP) | €13.40 / mo (~$14.50) | **₹1,220** | `https://www.hetzner.com/cloud` | Oct 14, 2026 |
| **GPU Inference Tier** | **RunPod Serverless GPU** (RTX 4090 24GB @ $0.00022/sec active compute. 1,000 queries $\times$ 10s = 10,000s/day = $66/mo) | $66.00 / mo | **₹5,540** | `https://www.runpod.io/pricing` | Oct 14, 2026 |
| **Offsite Encrypted Backups** | **Cloudflare R2 Object Storage** (10 GB storage + zero egress fees) | $0.15 / mo (Free tier covers up to 10GB) | **₹15** | `https://www.cloudflare.com/developer-platform/r2/` | Oct 14, 2026 |
| **Domain & DNS Security** | **Cloudflare Pro / Registrar** (Automated DDoS protection, WAF, DNS-01 ACME) | Free Tier ($0.00) | **₹0** | `https://www.cloudflare.com/plans/` | Oct 14, 2026 |
| **Uptime Monitoring & Alerts** | **Better Stack / Uptime Kuma** (Heartbeats, SSL probe, Telegram/SMS alerts) | Free Tier ($0.00) | **₹0** | `https://betterstack.com/pricing` | Oct 14, 2026 |
| **Emergency Contingency Buffer** | Compute elasticity spike buffer | $5.00 / mo | **₹425** | Reserved Buffer | Oct 14, 2026 |
| **TOTAL MONTHLY EXPENDITURE** | **High-Availability Cloud AI Stack** | **$85.65 / mo** | **₹7,200 / mo** | *(Well inside ₹25,000 limit; ₹17,800 monthly reserve)* | Oct 14, 2026 |

---

## 4. Keeping the Data Safe (Security & Backup Architecture)

1. **Database Backups:**
   - **Mechanism:** Automated daily `pg_dump` compressed with AES-256 GPG encryption (`backup_db.py`).
   - **Destination:** Uploaded immediately to Cloudflare R2 bucket (S3-compatible, multi-region geographic redundancy) and locally retained on the last 7 daily rolling snapshots.
   - **Automated Restore Drill:** A weekly cron job restores the latest dump into a temporary ephemeral container, executes `SELECT count(*) FROM cases;`, validates table parity, and alerts the team on failure.
2. **Secrets & Key Protection:**
   - No plaintext passwords or tokens in code or Git. All secrets injected via `.env` loaded into memory.
   - In production, managed via Docker secrets or Doppler/Vault.
3. **Server Access Control:**
   - Root password login disabled (`PermitRootLogin no`).
   - SSH strictly key-based (ED25519) on custom port.
   - UFW firewall permits only ports 80, 443, and WireGuard/Tailscale. All database ports are strictly bound to internal Docker bridge network (`127.0.0.1`).

---

## 5. Monitoring & Incident Alerting

- **Application Health:** Prometheus agent collects CPU, RAM, disk I/O, GPU VRAM, and HTTP status codes.
- **External Probing:** Better Stack / Uptime Kuma checks `https://app.example.in/health` every 60 seconds from 3 geographic nodes.
- **SSL Tracking:** Dedicated SSL expiry alert triggers at 21, 14, and 7 days.
- **Alert Dispatch:** Critical incidents trigger immediate Telegram and WhatsApp webhook notifications to the engineering team.

---

## 6. Moving Day Migration Plan (Zero Data Loss)

1. **T-48h (DNS TTL):** Lower DNS TTL for `app.example.in` to 300 seconds (5 minutes).
2. **T-24h (Staging Prep):** Deploy `docker-compose.yml` on the new Hetzner server; verify containers, Caddy SSL issuance, and GPU serverless connectivity.
3. **T-0 (Maintenance Window - 9:00 PM Sunday):**
   - Place frontend in maintenance mode.
   - Stop backend write traffic on the office server.
   - Run final database export: `pg_dump -Fc -v -h localhost -U app_user app_db > final_migration.dump`.
   - Transfer dump securely to cloud server via `rsync -avz -e ssh`.
   - Restore database: `pg_restore -d app_db final_migration.dump`.
   - Verify record counts and run smoke tests against backend health check.
   - Update DNS record to Hetzner public IP.
4. **Estimated Total Downtime:** **Under 12 minutes**.
