# Knowledge Graph Modeling of Tacit Underwriting Reasoning

**Author / Candidate:** AI Knowledge Graph & Cloud Engineering Candidate  
**Assessment Target:** Question 1 — Modeling the Loan Officer's Judgment in Python  
**Submission Date:** October 2026  
**Intended Format:** Markdown-to-PDF / ChatGPT Executive Report Export  

---

## Executive Summary

When a seasoned loan officer reviews two small-business loan applications that appear identical on standard underwriting forms, her decision is rarely guided by high-level numbers like Credit Score or Collateral Valuation. Instead, she uncovers subtle qualitative and structural details—clues that novice underwriters skim past—and maps them through her **unwritten tacit domain knowledge** to forecast whether the business can service senior debt under stress.

This report presents a complete, production-ready **Cognitive Knowledge Graph (KG)** developed in Python (`NetworkX`). The graph explicitly models how minor application signals connect through tacit domain facts to downstream financial consequences, creating an interpretable, auditable reasoning path from application form to final credit decision.

---

## 1. Case Study Definition: The Two Borrowers

Both applicants request **\$250,000 for a 3-year term** to fund business expansion:

| Underwriting Parameter | Applicant A: Apex Logistics Ltd. | Applicant B: Beacon Precision Ltd. | Beginner Interpretation |
|---|---|---|---|
| **Stated Business** | Refrigerated Food Transport & Wholesale | Precision CNC Tooling for Medical & Aerospace | Both are established industrial businesses |
| **Requested Loan** | \$250,000 (36-month amortization) | \$250,000 (36-month amortization) | Identical capital requirement |
| **Credit Score** | **742** (Prime) | **738** (Prime) | Both borrowers have exemplary credit histories |
| **Collateral Offered** | \$320,000 (Refrigerated Fleet & Stock) | \$310,000 (5-Axis DMG Mori CNC Machinery) | Both offer >120% Loan-to-Value (LTV) |
| **Historical DSCR** | 1.35x | 1.28x | Both demonstrate sufficient historical debt service |
| **The "Minor" Detail** | **84% of revenue tied to a single client (TitanMart)**; historical DSO is 45 days. | **Q2 Cash Dip (-\$65k)**; revenue spread across 22 clients (top client is 9%). | Beginner sees TitanMart as a "prestigious blue-chip client" and views Beacon's cash dip as "financial distress". |
| **Officer's Decision** | **DECLINED (REJECT)** | **APPROVED** | **Opposing verdicts on identical standard metrics** |

---

## 2. Why Beginners Skim and Seasoned Officers Intervene

### Application A: The Illusion of Security
A junior analyst looks at Apex Logistics and sees a **742 credit score**, a **\$320,000 fleet of trucks**, and an **84% relationship with retail titan TitanMart**. To the beginner, TitanMart represents security and guaranteed revenue.

**The Seasoned Officer's Tacit Knowledge:**
1. TitanMart recently underwent a highly leveraged private-equity buyout.
2. TitanMart's new management unilaterally extended vendor payment terms from 45 days to **90–120 days** while demanding mandatory **12% supplier discounts**.
3. Apex's working capital cannot bridge a 90-day receivable cycle. An extension of 45 days locks up **\$210,000** in uncollected cash.
4. Apex operates with zero pricing power (monopsony dependency). If Apex resists, TitanMart will replace them; if Apex complies, Debt Service Coverage (DSCR) collapses from **1.35x to 0.38x**.
5. Secondary market recovery: Auctioning refrigerated vans yields a **40% haircut** due to cold-chain refrigeration re-fitting costs, reducing true collateral recovery to <\$190,000.

### Application B: The "Blemish" That Conceals a Moat
A junior analyst looks at Beacon Precision and flags a **temporary cash reduction of \$65,000 in Q2**, warning of operational bleeding.

**The Seasoned Officer's Tacit Knowledge:**
1. The \$65,000 cash outlay was not operational loss; it was upfront tooling and **ISO-13485 (Medical Device) regulatory qualification audits**.
2. Medical and aerospace components require 12 to 18 months of rigorous vendor qualification. Once certified, switching suppliers is prohibitively expensive for buyers.
3. Beacon has **22 diversified clients**, with no single client representing more than 9% of sales (Herfindahl-Hirschman Index < 0.12).
4. The completed audit unlocked signed, binding purchase orders starting in Q3, increasing forward-looking DSCR to **2.15x**.
5. The DMG Mori 5-axis CNC machining center has active global liquidity and maintains **85%+ resale value**.

---

## 3. Cognitive Knowledge Graph Architecture

Rather than a simple flat ontology, the graph is organized into five causal layers:

```
┌────────────────────────────────────────────────────────┐
│               LAYER 1: APPLICATION FACTS               │
│  [Apex: 84% TitanMart Rev]   [Beacon: Q2 Cash Dip / ISO]│
└───────────────────────────┬────────────────────────────┘
                            │ :triggers_tacit_knowledge
┌───────────────────────────▼────────────────────────────┐
│          LAYER 2: TACIT DOMAIN KNOWLEDGE               │
│  [TitanMart PE Squeeze]      [ISO-13485 Regulatory Moat]│
└───────────────────────────┬────────────────────────────┘
                            │ :infers
┌───────────────────────────▼────────────────────────────┐
│          LAYER 3: INFERRED ASSESSMENTS                 │
│  [Monopsony Fragility]       [High Customer Stickiness] │
└───────────────────────────┬────────────────────────────┘
                            │ :leads_to_consequence
┌───────────────────────────▼────────────────────────────┐
│         LAYER 4: FINANCIAL CONSEQUENCES                │
│  [DSO 90d / DSCR 0.38x]      [Contracted Cashflow Surge]│
└───────────────────────────┬────────────────────────────┘
                            │ :determines_risk
┌───────────────────────────▼────────────────────────────┐
│           LAYER 5: REPAYMENT RISK & VERDICT            │
│  [Severe Default Risk]       [Low Default / High Buffer]│
│  ==> DECISION: REJECT        ==> DECISION: APPROVE      │
└────────────────────────────────────────────────────────┘
```

---

## 4. Graph Execution & Traversal Results

When the graph is queried for the causal reasoning chain connecting the minor application fact to the underwriting outcome, the reasoning engine traverses the multi-hop paths:

### Traversal Path 1: Apex Logistics (Rejection Audit Trail)
```text
(ApplicationFact: "84% Revenue via Retailer TitanMart")
  --[triggers_tacit_knowledge]--> "Officer matches stated buyer name against recent supply-chain distress reports"
==> (TacitKnowledge: "TitanMart PE Restructuring & Margin Squeeze")

(TacitKnowledge: "TitanMart PE Restructuring & Margin Squeeze")
  --[infers]--> "High concentration + predatory buyer behavior = extreme financial fragility"
==> (InferredAssessment: "Monopsony Price-Taker Fragility")

(InferredAssessment: "Monopsony Price-Taker Fragility")
  --[leads_to_consequence]--> "Unilateral term extension directly drains working capital cash reserves"
==> (FinancialConsequence: "Working Capital Freeze & DSCR Collapse")

(FinancialConsequence: "Working Capital Freeze & DSCR Collapse")
  --[determines_risk]--> "Insufficient operating cash flows to service senior bank debt"
==> (RepaymentRisk: "Severe Default & Illiquidity Risk")

(RepaymentRisk: "Severe Default & Illiquidity Risk")
  --[justifies_decision]--> "Officer rejects due to unhedged single-customer monopsony and impending liquidity freeze"
==> (Decision: "DECISION: REJECT APPLICATION")
```

### Traversal Path 2: Beacon Precision (Approval Audit Trail)
```text
(ApplicationFact: "Q2 Operating Cash Dip (-$65,000)")
  --[triggers_tacit_knowledge]--> "Officer recognizes Q2 cash expense as an essential moat-building capital investment rather than operational bleeding"
==> (TacitKnowledge: "ISO-13485 High Switching-Cost Moat")

(TacitKnowledge: "ISO-13485 High Switching-Cost Moat")
  --[infers]--> "Certified component status insulates supplier from customer churn"
==> (InferredAssessment: "High Customer Retention & Pricing Power")

(InferredAssessment: "High Customer Retention & Pricing Power")
  --[leads_to_consequence]--> "Secured purchase orders translate into high-margin operating cash flows"
==> (FinancialConsequence: "Contracted Cashflow Expansion & DSCR > 2.1x")

(FinancialConsequence: "Contracted Cashflow Expansion & DSCR > 2.1x")
  --[determines_risk]--> "High forward-looking debt service coverage creates safety buffer"
==> (RepaymentRisk: "Robust Debt-Service Capacity (Low Risk)")

(RepaymentRisk: "Robust Debt-Service Capacity (Low Risk)")
  --[justifies_decision]--> "Officer approves based on verified regulatory moat, customer diversification, and strong cash conversion"
==> (Decision: "DECISION: APPROVE APPLICATION")
```

---

## 5. Deliberate Modeling Choices & Scope Note

### What Was Included
1. **Explicit Causal Predicates:** Relationships are not generic links (`:related_to`); they are semantically explicit (`:triggers_tacit_knowledge`, `:leads_to_consequence`, `:justifies_decision`).
2. **Dynamic Forward-Looking Indicators:** Forward-looking DSCR projections and working capital drag were favored over historical ratios.
3. **Counterparty Risk Modeling:** The health of the borrower's principal client is treated as an active variable in the graph.

### What Was Excluded
1. **Balance Sheet Granularity:** Trivial line items (e.g., office stationery depreciation, individual utility bills) were excluded to preserve high signal-to-noise ratio.
2. **Probabilistic Black Boxes:** We avoided continuous Bayesian probability tables, favoring human-readable ontological reasoning that can be defended before credit risk committees.
3. **Subjective Character Metrics:** Personal rapport and borrower personality were strictly excluded to ensure compliance with anti-bias and fair lending regulations.

---

## 6. Verification and Test Suite

The solution includes a full test suite built in `pytest`:
- **Topological Integrity:** Verifies all 22 nodes and 21 directed edges.
- **Layer Coverage:** Confirms presence of all cognitive layers from Facts to Decisions.
- **Causal Path Guarantees:** Validates unbroken directed traversal paths from application clues to outcomes.
- **Export Formats:** Verifies high-resolution PNG visualization rendering and standardized JSON exports.

```bash
$ pytest question_1_knowledge_graph/test_knowledge_graph.py -v
============================== 5 passed in 0.79s ==============================
```

---

## Conclusion
A knowledge graph that stores facts simply tells us *what is*. A knowledge graph that models judgment explains *what will happen if circumstances change*. By bridging the gap between stated application facts and unwritten market realities, this implementation transforms credit underwriting from a backward-looking checklist into an interpretable cognitive reasoning engine.
