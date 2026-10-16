# AI Knowledge Graph & Cloud Engineering Production Submission

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/pytest-8%20passed-brightgreen.svg)]()

This repository contains the complete, production-grade solutions for the **AI Knowledge Graph & Cloud Engineering Internship Assignment** (Deadline: October 19, 2026).

---

## 📂 Repository Structure & Deliverables

```
├── question_1_knowledge_graph/            # QUESTION 1: KNOWLEDGE GRAPH
│   ├── loan_reasoning_graph.py            # Production NetworkX KG & multi-hop reasoning engine
│   ├── test_knowledge_graph.py            # Unit test suite (5 passed)
│   ├── note_on_modeling.md                # Required half-page note on modeling & scope
│   ├── loan_reasoning_graph.png           # High-resolution visual export of the reasoning graph
│   ├── loan_reasoning_graph.json          # Standardized graph topology export
│   ├── reasoning_audit_report.txt         # Plaintext cognitive audit trail
│   ├── Q1_KNOWLEDGE_GRAPH_PRESENTATION.md # Ready for ChatGPT -> PDF export
│   └── README.md                          # Detailed Q1 instructions
│
├── question_2_cloud/                      # QUESTION 2: CLOUD ENGINEERING
│   ├── part_a_incident_analysis/          # Part A: Broken Padlock Incident Investigation
│   │   ├── incident_report.md             # Complete root-cause analysis (Checks 1-6)
│   │   └── Q2_PART_A_PRESENTATION.md      # Ready for ChatGPT -> PDF export
│   │
│   ├── part_b_cloud_migration/            # Part B: Cloud Migration Plan (200 Users, <₹25k/mo)
│   │   ├── cloud_migration_plan.md        # 1.5-page plan with exact GPU math & verified costs
│   │   └── Q2_PART_B_PRESENTATION.md      # Ready for ChatGPT -> PDF export
│   │
│   └── part_c_docker_infrastructure/      # Part C: Full Docker Implementation & Backups
│       ├── docker-compose.yml             # 5 App components + Caddy + GPU + Healthchecks
│       ├── Caddyfile                      # Automated HTTPS proxy configuration
│       ├── .env.example                   # Production secret configuration
│       ├── app/                           # Runnable application source code
│       │   ├── frontend/                  # Responsive web dashboard (HTML5/CSS3/JS/Nginx)
│       │   ├── backend/                   # High-performance FastAPI REST server
│       │   ├── worker/                    # Asynchronous Python task processor
│       │   └── ai_service/                # Llama 3.1 8B inference engine with GPU passthrough
│       ├── backup_scripts/                # Automated Daily DB Backup & 7-Day Retention
│       │   ├── backup_db.py               # Cross-platform Python backup manager
│       │   ├── backup_db.sh               # Linux bash cron backup script
│       │   └── test_backup.py             # Backup unit test suite (3 passed)
│       └── Q2_PART_C_PRESENTATION.md      # Ready for ChatGPT -> PDF export
│
├── diagrams/                              # ARCHITECTURAL DIAGRAMS & SKETCHES
│   ├── q1_graph_diagram.md                # Q1 Mermaid diagram & hand-drawn sketch guide
│   └── q2_cloud_diagram.md                # Q2 Mermaid diagram & hand-drawn sketch guide
│
├── roadmap.md                             # Deep-dive app walkthrough & non-AWS cloud deployment
├── how_i_worked.md                        # Note on AI tools, disagreements, and fact vs reasoning
├── contact.txt                            # Candidate contact info & interview availability
└── problem.md                             # Original assignment specification
```

---

## ⚡ Quick Start: Verify Everything Locally

### 1. Test Question 1 (Knowledge Graph):
```bash
# Execute reasoning path traversal & generate visualization:
python question_1_knowledge_graph/loan_reasoning_graph.py

# Run unit tests:
pytest question_1_knowledge_graph/test_knowledge_graph.py -v
```

### 2. Test Question 2 Part C (Backup Manager & Retention):
```bash
# Run unit tests for 7-day backup retention rotation:
pytest question_2_cloud/part_c_docker_infrastructure/backup_scripts/test_backup.py -v
```

### 3. Launch Full Production Stack with Docker:
```bash
cd question_2_cloud/part_c_docker_infrastructure
cp .env.example .env
docker compose up -d --build
```
Access the application at `http://localhost` (or `https://app.example.in`).

---

## 📑 Summary of Key Findings

### Question 1: Knowledge Graph (Modeling Underwriting Judgment)
- **Apex Logistics (Rejected):** Stated 84% revenue via retailer TitanMart. The officer's tacit knowledge identifies TitanMart's private-equity buyout and aggressive 90-day payment term policy. An uncollected receivable cycle causes Debt Service Coverage (DSCR) to collapse from 1.35x to 0.38x $\implies$ **DECLINE**.
- **Beacon Precision (Approved):** Apparent Q2 cash dip was upfront investment in **ISO-13485 medical device qualification**. Once certified across 22 clients, high switching costs insulate Beacon from churn, surging forward DSCR to 2.15x $\implies$ **APPROVE**.

### Question 2 Part A: Padlock Failure Diagnosis
- **The Culprit:** The replacement broadband router installed in September intercepted incoming WAN port 80 traffic with its own web administration portal (`micro_httpd 401 Unauthorized`), blocking Let's Encrypt ACME HTTP-01 renewal challenges.
- **The Fix:** Disable WAN remote router management, set static DHCP reservation, forward ports 80 & 443 to the server, and restart Caddy.

### Question 2 Part B: Cloud Migration Plan (200 Users, <₹25,000/mo)
- **Selected Architecture:** **Hetzner Cloud VPS (₹1,220/mo)** + **RunPod Serverless GPU / Tailscale Hybrid (₹5,540/mo)** + **Cloudflare R2 Backups (₹15/mo)**.
- **Total Cost:** **₹7,200/month** (Leaves **₹17,800/month buffer** within the ₹25,000 cap).
- **GPU Capacity:** Llama 3.1 8B in 4-bit precision occupies **7.2 GB VRAM**, leaving 16.8 GB free for **vLLM PagedAttention continuous batching**, easily handling 10-query spikes with sub-2-second streaming latency.

---

## 📄 Generating PDF Reports via ChatGPT

Each problem has a dedicated presentation file engineered specifically to be pasted into ChatGPT (or converted via Markdown-to-PDF / Pandoc) to generate executive PDF reports:
1. `question_1_knowledge_graph/Q1_KNOWLEDGE_GRAPH_PRESENTATION.md`
2. `question_2_cloud/part_a_incident_analysis/Q2_PART_A_PRESENTATION.md`
3. `question_2_cloud/part_b_cloud_migration/Q2_PART_B_PRESENTATION.md`
4. `question_2_cloud/part_c_docker_infrastructure/Q2_PART_C_PRESENTATION.md`

Simply copy the content of any of these files into ChatGPT and ask: *"Please format this markdown into a clean, executive PDF report."* or use VS Code's "Markdown PDF" extension.

---

## 📞 Interview Scheduling
Contact details and preferred call availability are provided in [`contact.txt`](contact.txt).
