# System Architecture & Non-AWS Action Roadmap

**Project:** AI Knowledge Graph & Cloud Engineering Production Deployment  
**Objective:** Complete operational guide to running, explaining, and deploying the codebase without AWS lock-in.

---

## 🧭 Table of Contents
1. [Deep-Dive Application Walkthrough (For Your Interview Call)](#1-deep-dive-application-walkthrough)
2. [Why We Avoid AWS & Modern Non-AWS Cloud Alternatives](#2-why-we-avoid-aws--modern-non-aws-cloud-alternatives)
3. [Step-by-Step: How to Run the Codebase Locally (Two Ways)](#3-step-by-step-how-to-run-the-codebase-locally)
   - [Method A: Standalone Python (No Docker Required)](#method-a-standalone-python-fastest-for-testing)
   - [Method B: Full Containerized Stack (Docker Compose)](#method-b-full-containerized-production-stack)
4. [Deployment Roadmap Without AWS (Cost: ₹7,200/mo vs Budget: ₹25,000/mo)](#4-deployment-roadmap-without-aws)
5. [Interview Walkthrough Cheat Sheet ("What-If" Questions)](#5-interview-walkthrough-cheat-sheet)

---

## 1. Deep-Dive Application Walkthrough

To explain this application confidently on your 30-minute evaluation call, remember that the system is engineered around **one core principle: strict separation between deterministic business state and non-deterministic AI inference**.

### The 5 Architectural Layers:

```
[ Visitor Browser ] 
       │ (HTTPS / Port 443)
       ▼
[ Caddy Reverse Proxy ]
  ├── /api/* ──► [ FastAPI Backend ] ──► [ PostgreSQL 16 ] (Encrypted Case Notes)
  │                      │
  │                      ├──► [ Redis Broker ] ──► [ Background Worker ]
  │                      │                                 │
  │                      └──────────► [ AI Engine ] ◄──────┘
  │                                   (Llama 3.1 8B)
  └── /* ──────► [ Frontend UI (Nginx) ]
```

1. **Caddy Edge Proxy:**
   - **What it does:** Sits at the public network boundary (ports 80 and 443).
   - **Why Caddy over Nginx/Apache:** Caddy natively provisions and auto-renews TLS certificates from Let's Encrypt / ZeroSSL without requiring external certbot cron jobs. It terminates TLS, compresses responses (Zstandard/Gzip), injects security headers, and reverse-proxies `/api` traffic to FastAPI and `/` traffic to the static web client.

2. **Frontend UI (Web Client):**
   - **What it does:** A clean, responsive single-page web portal where caseworkers manage sensitive client notes and interact with the AI assistant.
   - **Privacy feature:** Pseudonymizes client records (e.g. `Client-4819`) to prevent Personal Identifiable Information (PII) leakage.

3. **Backend API (FastAPI):**
   - **What it does:** Provides high-concurrency asynchronous REST endpoints.
   - **Key responsibilities:**
     - `/health`: Actively probes database and Redis connectivity.
     - `/api/cases`: Validates payloads using Pydantic, persists records in PostgreSQL, and enqueues background summarization jobs into Redis.
     - `/api/ask`: Proxies user questions to the AI microservice with token streaming.

4. **PostgreSQL 16 & Redis Message Broker:**
   - **PostgreSQL:** The single source of truth for ACID-compliant structured data. Stored on a dedicated named Docker volume (`caresync_postgres_data`).
   - **Redis:** Decouples user-facing web requests from heavy AI background jobs. If a caseworker saves 50 case notes at once, Redis buffers the queue so the web UI remains instantly responsive.

5. **Background Worker & AI Inference Engine (Llama 3.1 8B):**
   - **Background Worker:** A headless Python consumer that pulls jobs from Redis, prompts the AI model, and saves summaries back to PostgreSQL.
   - **AI Microservice:** Exposes an OpenAI-compatible `/v1/chat/completions` API. In production, it leverages NVIDIA GPUs (24GB VRAM) running 4-bit quantized Llama 3.1 8B with **PagedAttention continuous batching**. On developer laptops without an NVIDIA GPU, it gracefully switches to an intelligent simulation mode so every team member can develop locally.

---

## 2. Why We Avoid AWS & Modern Non-AWS Cloud Alternatives

The problem statement asks for a reliable cloud plan within **₹25,000/month**. 

### Why Traditional AWS Fails for this Budget:
1. **GPU Pricing:** An AWS `g5.xlarge` (NVIDIA A10G 24GB) costs **~$1.006/hour = ~$734/month (~₹61,000/month)** on on-demand pricing—**more than double the entire monthly budget**!
2. **Hidden Egress & NAT Gateway Fees:** AWS charges \$0.09/GB for data transfer out plus \$32/mo for NAT Gateways.
3. **Complexity Overhead:** Requires configuring IAM roles, VPC peering, Application Load Balancers, and CloudWatch.

### Recommended Non-AWS Alternatives:

| Cloud Provider | Role in Our Stack | Specs | Price (INR) | Why It Wins Over AWS |
|---|---|---|---|---|
| **Hetzner Cloud** | App Server + DB + Proxy + Worker | CPX31 (4 AMD vCPU, 8 GB RAM, 160 GB NVMe SSD) | **₹1,220 / mo** (€13.40) | 99.99% SLA, includes 20 TB egress free, zero hidden charges. |
| **RunPod Serverless** | AI Inference (Llama 3.1 8B) | NVIDIA RTX 4090 (24GB VRAM) @ \$0.00022 / active second | **₹5,540 / mo** ($66.00 for 1,000 queries/day) | Pay only when computing tokens. Zero idle GPU cost during nights and weekends. |
| **Vast.ai / Lambda Labs** | Alternative GPU Hosting | Dedicated RTX 3090/4090 24GB on-demand instance | **₹18,000–₹22,000 / mo** | 70% cheaper than AWS EC2 GPU instances. |
| **Cloudflare R2** | Offsite Encrypted DB Backups | 10 GB Object Storage (S3 API compatible) | **₹15 / mo** | **Zero egress fees**. Unlike AWS S3, downloading your backup is completely free. |
| **Tailscale / WireGuard** | Secure Hybrid Mesh Tunnel | Zero-Trust P2P Mesh VPN | **₹0 (Free tier)** | Connects cloud VPS directly to office GPU without exposing any router ports. |

---

## 3. Step-by-Step: How to Run the Codebase Locally

### Method A: Standalone Python (Fastest for Testing)

You can run both Question 1 and the test suites immediately without Docker:

#### 1. Test Question 1 (Knowledge Graph):
```powershell
# Run the knowledge graph engine, path tracing, and visual export:
python question_1_knowledge_graph/loan_reasoning_graph.py

# Run the automated unit tests:
python -m pytest question_1_knowledge_graph/test_knowledge_graph.py -v
```
*Outputs generated:* `loan_reasoning_graph.png`, `loan_reasoning_graph.json`, and `reasoning_audit_report.txt`.

#### 2. Test Question 2 Part C (Database Backup & Retention):
```powershell
# Run the automated backup test suite:
python -m pytest question_2_cloud/part_c_docker_infrastructure/backup_scripts/test_backup.py -v
```

---

### Method B: Full Containerized Production Stack (Docker Compose)

To launch the full 6-container production app on your machine or cloud server:

#### 1. Navigate to the Infrastructure Directory:
```bash
cd question_2_cloud/part_c_docker_infrastructure
```

#### 2. Initialize Environment Secrets:
```bash
cp .env.example .env
```

#### 3. Build and Spin Up All Services:
```bash
docker compose up -d --build
```

#### 4. Verify Active Health Checks:
```bash
docker compose ps
```
*Expected status:* All containers (`caresync_caddy`, `caresync_frontend`, `caresync_backend`, `caresync_postgres`, `caresync_redis`, `caresync_ai_model`) should report `Up (healthy)`.

#### 5. Access the Running System:
- **Web Dashboard:** Open `http://localhost` (or `https://app.example.in` when DNS is pointed).
- **Backend Health Check:** `curl http://localhost:8000/health` $\to$ `{"status":"ok","database":"ok","redis":"ok"}`.
- **AI Model Status:** `curl http://localhost:8001/health` $\to$ `{"status":"ok","model":"llama-3.1-8b-instruct"}`.

#### 6. Execute an Automated Database Backup:
```bash
python backup_scripts/backup_db.py
# Or on Linux:
bash backup_scripts/backup_db.sh
```

---

## 4. Deployment Roadmap Without AWS

If you are asked on the call: *"How would you deploy this tomorrow for our 200 users without AWS?"*, here is your exact, step-by-step roadmap:

### Step 1: Provision the Application Host (Hetzner Cloud)
1. Sign up on [Hetzner Cloud](https://www.hetzner.com/cloud).
2. Create a new Server:
   - **Location:** Falkenstein (EU) or Ashburn (US).
   - **OS:** Ubuntu 24.04 LTS.
   - **Type:** CPX31 (4 vCPU AMD, 8 GB RAM, 160 GB NVMe) — **€13.40/month (~₹1,220 INR)**.
   - **SSH Key:** Add your ED25519 public key.
3. Configure UFW Firewall on Hetzner:
   - Allow ports `22` (SSH), `80` (HTTP), and `443` (HTTPS).

### Step 2: Provision GPU Inference (RunPod Serverless or Office GPU via Tailscale)
**Option 1: Serverless GPU on RunPod (Recommended):**
- Deploy a pre-configured Llama-3.1-8B-Instruct endpoint on RunPod Serverless with 4-bit AWQ.
- Copy the endpoint URL and API key into `.env` under `AI_SERVICE_URL`.
- Cost: ₹0 when idle; ₹5,540/month during active 1,000 queries/day.

**Option 2: Hybrid via Tailscale (Zero Router Forwarding):**
- Install Tailscale on the office Ubuntu GPU computer: `curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up`.
- Install Tailscale on the Hetzner VPS: `sudo tailscale up`.
- The Hetzner VPS can now communicate directly with the office GPU over the private encrypted IP (e.g. `http://100.x.y.z:8001`) with **zero public router ports opened**. This completely eliminates the router issue from Part A!

### Step 3: Deploy via Git & Docker Compose
```bash
git clone <YOUR_REPO_URL>
cd Knowledge-Graph-And-Cloud-Engineering/question_2_cloud/part_c_docker_infrastructure
cp .env.example .env
docker compose up -d
```

### Step 4: DNS Cutover on Cloudflare
1. In Cloudflare DNS, add an `A` record:
   - `app.example.in` $\to$ `<Hetzner_Public_IP>` (Proxy status: Proxied or DNS only).
2. Caddy automatically contacts Let's Encrypt, completes the TLS handshake, and brings up the green padlock in the browser.

### Step 5: Configure Nightly Backup Cron
Add a cron job on the Hetzner server:
```bash
0 2 * * * /usr/bin/python3 /opt/caresync/backup_scripts/backup_db.py >> /var/log/caresync_backup.log 2>&1
```

---

## 5. Interview Walkthrough Cheat Sheet ("What-If" Questions)

Be prepared to answer these common technical curveballs:

| "What-If" Scenario | Your Confident Answer |
|---|---|
| *"What if the budget is cut from ₹25,000 to ₹5,000 per month?"* | Use Option C-Hybrid: Keep the AI model on the office 24GB GPU, host the web/database on a Hetzner CX22 server (€3.79/mo = ₹350 INR), and bridge them via **free Tailscale mesh VPN**. Total cloud cost is under **₹1,000/month**! |
| *"What if 50 users submit a prompt at the exact same second?"* | With continuous batching (PagedAttention in vLLM), requests don't queue sequentially. The GPU batches attention states across tensor cores, returning the first tokens to all users in under 2.5 seconds via streaming SSE. |
| *"What if the loan applicant has a 780 credit score but high customer concentration?"* | The knowledge graph proves that credit score is a lagging indicator. Even with a 780 credit score, if 85% of revenue is tied to a distressed buyer who extends payment terms by 45 days, liquidity dries up and the firm will default on senior debt regardless of past creditworthiness. |
| *"Why didn't you use Celery for the background worker?"* | For a 200-user system, a lightweight Python worker with Redis lists (`blpop`) gives sub-millisecond task dispatch without the heavy dependency footprint, broker complexity, and RPC serialization overhead of Celery. |
