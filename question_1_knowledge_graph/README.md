# Question 1: Knowledge Graph for Loan Underwriting Reasoning

This directory contains the production-ready implementation of a **Cognitive Underwriting Knowledge Graph** that models how a seasoned loan officer evaluates two seemingly identical small-business loan applications using tacit domain knowledge.

---

## 📌 Executive Summary

Two borrowers present nearly identical quantitative fundamentals:
- **Requested Amount:** $250,000 for 3 years
- **Credit Score:** 742 (Firm A) vs. 738 (Firm B)
- **Collateral:** $320,000 (Firm A) vs. $310,000 (Firm B)
- **Historical DSCR:** ~1.30x

Yet the loan officer **rejects Firm A (Apex Logistics)** and **approves Firm B (Beacon Precision)**.

The knowledge graph models how subtle details on the application connect through **unwritten domain knowledge** to decisive consequences on debt repayment:
1. **Firm A's Flaw:** 84% revenue concentration with a retail conglomerate currently undergoing private-equity restructuring, extending payment terms from 45 to 90+ days. This locks up working capital and causes Debt Service Coverage (DSCR) to collapse to 0.38x.
2. **Firm B's Strength:** A recent temporary cash drop was not operational bleeding, but upfront funding for **ISO-13485 medical device certification** and precision tooling across 22 clients (top client < 9%). This creates high customer switching costs, unlocking secured purchase orders and driving forward-looking DSCR to 2.15x.

---

## 📂 Directory Contents

| File | Description |
|---|---|
| [`loan_reasoning_graph.py`](loan_reasoning_graph.py) | Full Python knowledge graph built with `NetworkX`. Encodes nodes, multi-hop reasoning rules, path tracing, and visual export. |
| [`test_knowledge_graph.py`](test_knowledge_graph.py) | Unit test suite using `pytest` verifying graph topology, reasoning path completeness, and decision outcomes. |
| [`note_on_modeling.md`](note_on_modeling.md) | The required half-page note explaining modeling rationale and what was intentionally omitted. |
| [`loan_reasoning_graph.png`](loan_reasoning_graph.png) | High-resolution publication-quality visual rendering of the knowledge graph (Facts $\to$ Tacit Knowledge $\to$ Consequences $\to$ Decisions). |
| [`loan_reasoning_graph.json`](loan_reasoning_graph.json) | Exported graph structure (nodes & directed edges) for interoperability. |
| [`reasoning_audit_report.txt`](reasoning_audit_report.txt) | Generated plain-text audit trail showing the multi-hop cognitive traversal. |
| [`Q1_KNOWLEDGE_GRAPH_PRESENTATION.md`](Q1_KNOWLEDGE_GRAPH_PRESENTATION.md) | Formatted markdown document ready for ChatGPT or any Markdown-to-PDF engine to export a presentation PDF. |

---

## 🚀 How to Run the Code

### 1. Requirements
- Python 3.9+
- `networkx`
- `matplotlib`
- `pytest`

### 2. Execution Commands

To build the graph, perform path traversal, print the audit report, and generate the PNG & JSON exports:
```bash
python question_1_knowledge_graph/loan_reasoning_graph.py
```

To run the automated test suite:
```bash
pytest question_1_knowledge_graph/test_knowledge_graph.py -v
```

---

## 🧠 Cognitive Architecture: Facts vs. Reasoning

Unlike standard databases that store tabular facts, this graph implements a **Multi-Layer Semantic Network**:
```text
[ Application Fact ]
         │
         ▼  (:triggers_tacit_knowledge)
[ Tacit Domain Knowledge ] (Officer's mental model / unwritten industry dynamics)
         │
         ▼  (:infers)
[ Inferred Assessment ] (Pricing power, monopsony risk, customer stickiness)
         │
         ▼  (:leads_to_consequence)
[ Financial Consequence ] (Working capital freeze, DSCR change, liquidity impact)
         │
         ▼  (:determines_risk)
[ Repayment Risk ] (Default probability over loan tenure)
         │
         ▼  (:justifies_decision)
[ Underwriting Decision ] (Approve vs Reject)
```

This structure makes every underwriting verdict **fully explainable, auditable, and resilient to regulatory scrutiny**.
