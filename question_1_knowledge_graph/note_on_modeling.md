# Modeling the Loan Officer's Judgment: Rationale & Scope Note

**Candidate Submission — Question 1: Knowledge Graph**  
**Role:** AI Knowledge Graph & Cloud Engineering Intern  
**Scope:** Max Half-Page Note (Underwriting Modeling Decisions & Deliberate Exclusions)

---

### 1. Why I Modeled the Judgment This Way
A standard database or naive knowledge graph models *static facts*: borrower $A$ has credit score $X$, collateral $Y$, and revenue $Z$. However, credit underwriting is fundamentally an exercise in **counterfactual causal projection**: estimating whether future cash flows will cover debt obligations when subjected to real-world friction. 

To capture the officer's mental model, I structured the graph as a **five-layer cognitive hierarchy**:
1. **Application Facts** (explicit data in the form, e.g., *84% revenue via TitanMart* vs. *Q2 cash dip for ISO-13485 audit*).
2. **Tacit Domain Knowledge** (the officer's unstated mental ontology, e.g., *TitanMart's private-equity buyout and aggressive payment-term extension* vs. *the high switching cost of medical device certification*).
3. **Inferred Assessments** (monopsony price-taker fragility vs. customer portfolio diversification).
4. **Financial Consequences** (multi-month working capital lockup / DSCR collapse vs. contracted high-margin cash expansion).
5. **Repayment Risk & Underwriting Decision** (high default probability $\rightarrow$ Decline vs. resilient debt service capacity $\rightarrow$ Approve).

By linking facts to decisions through explicit `:triggers_tacit_knowledge` and `:leads_to_consequence` edges, the graph preserves the **causal chain of reasoning**. We can traverse the graph using simple path-finding algorithms to generate a deterministic, transparent audit trail that answers *"Why was this decision reached?"* without relying on opaque black-box scoring.

---

### 2. What I Chose to Leave Out and Why
To keep the graph focused, explainable, and computationally tractable, I made three deliberate exclusions:

1. **Excluded Granular Financial Line Items (Balance Sheet Noise):**  
   *Why:* Real credit applications contain dozens of line items (depreciation schedules, utility bills, inventory sub-accounts). Incorporating all of them creates an intractable "hairball" graph where the decisive signal is lost in noise. I retained only the metrics that directly interact with liquidity and debt-service capacity (collateral, credit score, DSO, customer concentration, and non-recurring CapEx).
   
2. **Excluded Continuous Probabilistic Graphical Models (Bayesian Networks):**  
   *Why:* While credit risk involves probabilities, seasoned human underwriters do not calculate exact Bayesian posteriors in their heads; they employ **heuristic causal rules** (e.g., *"If single client > 70% and client is extending payment terms, cash buffer will evaporate"*). Modeling this as an ontological semantic graph rather than a continuous distribution keeps the reasoning human-interpretable and inspectable during committee review.

3. **Excluded Borrower Relationship / Social Capital Factors:**  
   *Why:* Factors like *"how friendly the owner seemed"* or subjective personal rapport introduce underwriting bias and regulatory compliance risks (e.g., Fair Lending / Equal Credit Opportunity laws). Restricting the graph strictly to verifiable business relationships, counterparty health, and supply-chain dynamics ensures that the model reflects defensible, auditable financial prudence.
