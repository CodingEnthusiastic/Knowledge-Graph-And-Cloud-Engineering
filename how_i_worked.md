# How I Worked: Methodology, Progress & Reflection

**Assignment Submission:** AI Knowledge Graph & Cloud Engineering Internship  
**Candidate Note:** Max 1-Page Summary on Engineering Process, AI Collaboration & Concept Reflection  

---

### 1. AI Tools Utilized & A Key Technical Disagreement
During this project, I used AI assistance (specifically Claude and ChatGPT) primarily as a pair-programmer for boilerplate scaffolding, rapid regex syntax verification, and exploratory brainstorming of edge-case scenarios.

**A Crucial Instance Where I Rejected AI Suggestions:**
When initially designing the Knowledge Graph for Question 1, the AI assistant proposed a heavy semantic web stack: setting up an Apache Jena Fuseki triplestore, translating data into complex OWL (Web Ontology Language) classes with RDFLib, and executing SPARQL queries. 

**Why I Rejected It:**  
1. **Unnecessary Complexity:** In an underwriting context where human loan officers and committee members need clear explanations during a 30-minute review call, a SPARQL endpoint is opaque and difficult to trace visually.
2. **Loss of Explanatory Power:** A standard RDF graph treats relationships as static predicate triples (`:Apex :hasCustomer :TitanMart`). It struggles to capture dynamic multi-hop causal reasoning—such as how an unwritten private-equity buyout collapses debt-service coverage (DSCR).
3. **The Better Choice:** I discarded the AI's proposal and instead built a clean, object-oriented directed graph using Python's `NetworkX`. I modeled explicit cognitive layers (`ApplicationFact` $\to$ `TacitKnowledge` $\to$ `InferredAssessment` $\to$ `FinancialConsequence` $\to$ `RepaymentRisk` $\to$ `Decision`). This gave us complete transparency, multi-hop path tracing, and high-resolution visual exports that anyone on the committee can immediately understand.

Similarly, in Question 2 Part B, the AI initially suggested a default AWS architecture (`g5.xlarge` EC2 + RDS + ALB), which would have cost over **₹65,000/month**, blowing past the **₹25,000/month** budget. I rejected this and formulated an architecture combining **Hetzner Cloud** and **RunPod Serverless / Tailscale Hybrid**, which slashed the monthly cost to **₹7,200/month** while providing 99.99% availability.

---

### 2. Progress Log & Iteration Milestones

- **October 15, 2026:**
  - *Attempted:* Began with Question 2 Part A (padlock diagnosis). Initially looked at Caddy certificate renewal configs.
  - *Pivot:* Comparing Check 4 (`notAfter=Oct 12`) with Check 6 (`Server: micro_httpd` with `401 Unauthorized`) revealed the smoking gun: the new router installed in early September lacked port forwarding and was exposing its own admin portal on WAN port 80.
- **October 15, 2026:**
  - *Attempted:* Researched cloud hosting options for 200 users under ₹25,000/mo. Verified real-time pricing on Hetzner, RunPod, Vast.ai, and Cloudflare R2.
  - *GPU Math:* Computed memory and concurrency requirements for Llama 3.1 8B. Proved that 4-bit quantization reduces VRAM from 20.5 GB to 7.2 GB, enabling continuous batching via PagedAttention for simultaneous 10-query spikes.
- **October 15, 2026:**
  - *Attempted:* Designed Question 1 Knowledge Graph. Formulated the contrasting borrower case studies (Apex vs. Beacon). Built the NetworkX graph engine and multi-hop path-tracing audit trail.
  - *Testing:* Implemented automated unit test suites (`pytest`) verifying topological integrity and causal path completeness (5 passed).
- **October 16, 2026:**
  - *Implementation:* Built full production Docker Compose stack for Part C (FastAPI backend, PostgreSQL, Redis, Worker, AI Engine, Caddy TLS proxy) and created the cross-platform rolling 7-day database backup retention system (`backup_db.py` & `backup_db.sh`) with unit tests (3 passed).
  - *Documentation:* Authored dedicated presentation markdown files for all parts, architecture diagrams, and the non-AWS roadmap.

---

### 3. The Difference Between Storing Facts vs. Storing Reasoning

> **"A graph that stores facts simply maps static entities and their observed attributes, whereas a graph that stores reasoning captures the unstated causal mechanisms and domain heuristics that transform those observations into predictive judgments."**
