"""
Loan Underwriting Knowledge Graph: Modeling Reasoning and Tacit Judgment
========================================================================

This module models how a seasoned loan officer evaluates two seemingly identical
small-business loan applications by connecting subtle application facts with
unwritten domain knowledge (tacit knowledge) to reach opposing underwriting decisions.

Author: AI Knowledge Graph & Cloud Engineering Candidate
Date: October 2026
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LoanReasoningKG")


class NodeType(str, Enum):
    """Categorizes the cognitive layers of the knowledge graph."""
    BORROWER = "Borrower"
    APPLICATION_FACT = "ApplicationFact"          # Explicit stated data in form
    TACIT_KNOWLEDGE = "TacitKnowledge"            # Officer's unwritten industry expertise
    INFERRED_ASSESSMENT = "InferredAssessment"    # Intermediate cognitive deduction
    FINANCIAL_CONSEQUENCE = "FinancialConsequence"# Direct impact on cash flow / DSCR
    REPAYMENT_RISK = "RepaymentRisk"              # Final solvency & repayment outlook
    DECISION = "Decision"                        # Underwriting decision (Approve/Reject)


class RelationType(str, Enum):
    """Semantic relation types connecting graph nodes."""
    HAS_FACT = "has_stated_fact"
    TRIGGERS_TACIT_KNOWLEDGE = "triggers_tacit_knowledge"
    INFERS = "infers"
    LEADS_TO_CONSEQUENCE = "leads_to_consequence"
    DETERMINES_RISK = "determines_risk"
    JUSTIFIES_DECISION = "justifies_decision"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"


@dataclass
class GraphNode:
    """Represents a node in the reasoning graph."""
    node_id: str
    node_type: NodeType
    label: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.node_id,
            "type": self.node_type.value,
            "label": self.label,
            "description": self.description,
            "metadata": self.metadata,
        }


class LoanReasoningKnowledgeGraph:
    """
    A knowledge graph that encodes both explicit application facts and
    implicit cognitive reasoning paths used by experienced loan underwriters.
    """

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.nodes_registry: Dict[str, GraphNode] = {}

    def add_entity(self, node: GraphNode) -> None:
        """Register a node in the graph with rich semantic metadata."""
        self.nodes_registry[node.node_id] = node
        self.graph.add_node(
            node.node_id,
            type=node.node_type.value,
            label=node.label,
            description=node.description,
            metadata=node.metadata,
        )

    def add_relation(
        self,
        source_id: str,
        relation: RelationType,
        target_id: str,
        reasoning_rule: str,
        weight: float = 1.0,
    ) -> None:
        """Add a directed reasoning edge with explanation metadata."""
        if source_id not in self.graph:
            raise KeyError(f"Source node '{source_id}' does not exist in graph.")
        if target_id not in self.graph:
            raise KeyError(f"Target node '{target_id}' does not exist in graph.")

        self.graph.add_edge(
            source_id,
            target_id,
            relation=relation.value,
            rule=reasoning_rule,
            weight=weight,
        )

    def build_case_studies(self) -> None:
        """
        Populate the graph with two small-business loan applications:
        - Application A: Apex Logistics & Wholesale (Appears healthy, rejected on tacit insight)
        - Application B: Beacon Precision Tooling (Appears slightly blemished, approved on tacit insight)
        """
        logger.info("Building Knowledge Graph for Loan Underwriting Reasoning...")

        # ====================================================================
        # 1. APPLICATION A: APEX LOGISTICS (Rejected)
        # ====================================================================
        # Stated Baseline Metrics:
        # Credit: 742 | Collateral: $320k | Loan: $250k | Rev: $1.4M | Current DSCR: 1.35x
        apex = GraphNode(
            node_id="BORROWER_APEX",
            node_type=NodeType.BORROWER,
            label="Apex Logistics Ltd.",
            description="Regional refrigerated distribution supplier requesting $250k working capital.",
            metadata={"credit_score": 742, "requested_amount": 250000, "collateral_value": 320000},
        )
        self.add_entity(apex)

        # Baseline facts (Both applications share similar numbers)
        apex_credit = GraphNode(
            node_id="FACT_APEX_CREDIT",
            node_type=NodeType.APPLICATION_FACT,
            label="Prime Credit Score: 742",
            description="Owner personal credit score 742, clean payment history on small tier credit lines.",
        )
        apex_collateral = GraphNode(
            node_id="FACT_APEX_COLLATERAL",
            node_type=NodeType.APPLICATION_FACT,
            label="Collateral: $320,000",
            description="Refrigerated fleet and warehouse inventory pledged at 128% loan-to-value.",
        )
        # The seemingly innocuous detail that beginners miss or misunderstand as positive
        apex_anchor_client = GraphNode(
            node_id="FACT_APEX_CLIENT_CONCENTRATION",
            node_type=NodeType.APPLICATION_FACT,
            label="84% Revenue via Retailer TitanMart",
            description="Form detail: Long-standing supply contract delivering 84% of gross revenue to TitanMart Corp.",
        )
        apex_payment_terms = GraphNode(
            node_id="FACT_APEX_DSO",
            node_type=NodeType.APPLICATION_FACT,
            label="Accounts Receivable DSO: 45 Days",
            description="Form shows historical average collection period of 45 days.",
        )

        for n in [apex_credit, apex_collateral, apex_anchor_client, apex_payment_terms]:
            self.add_entity(n)
            self.add_relation(apex.node_id, RelationType.HAS_FACT, n.node_id, "Form declaration")

        # Officer's Tacit Knowledge (Not on any form)
        tacit_titanmart_reorg = GraphNode(
            node_id="TACIT_TITANMART_RESTRUCTURING",
            node_type=NodeType.TACIT_KNOWLEDGE,
            label="TitanMart PE Restructuring & Margin Squeeze",
            description="Unwritten industry intel: TitanMart was bought out by aggressive PE; currently unilaterally extending vendor payment terms to 90+ days and demanding 12% price cuts.",
        )
        tacit_fleet_depreciation = GraphNode(
            node_id="TACIT_COLD_CHAIN_DEPRECIATION",
            node_type=NodeType.TACIT_KNOWLEDGE,
            label="Specialized Chilled Fleet Illiquidity",
            description="Officer's market experience: Used refrigerated vans face 40% liquidation discount at auction; effective recoverable collateral is under $190k.",
        )
        self.add_entity(tacit_titanmart_reorg)
        self.add_entity(tacit_fleet_depreciation)

        self.add_relation(
            apex_anchor_client.node_id,
            RelationType.TRIGGERS_TACIT_KNOWLEDGE,
            tacit_titanmart_reorg.node_id,
            "Officer matches stated buyer name against recent supply-chain distress reports",
        )
        self.add_relation(
            apex_collateral.node_id,
            RelationType.TRIGGERS_TACIT_KNOWLEDGE,
            tacit_fleet_depreciation.node_id,
            "Officer adjusts paper collateral valuation based on secondary market auction data",
        )

        # Inferred Assessments
        inferred_apex_fragility = GraphNode(
            node_id="INFER_APEX_EXTREME_DEPENDENCY",
            node_type=NodeType.INFERRED_ASSESSMENT,
            label="Monopsony Price-Taker Fragility",
            description="Apex has zero pricing power. Inability to pass through cost inflation or resist contract renegotiation.",
        )
        self.add_entity(inferred_apex_fragility)
        self.add_relation(
            tacit_titanmart_reorg.node_id,
            RelationType.INFERS,
            inferred_apex_fragility.node_id,
            "High concentration + predatory buyer behavior = extreme financial fragility",
        )

        # Financial Consequences
        apex_cashflow_squeeze = GraphNode(
            node_id="CONSEQ_APEX_WORKING_CAPITAL_DEFICIT",
            node_type=NodeType.FINANCIAL_CONSEQUENCE,
            label="Working Capital Freeze & DSCR Collapse",
            description="Extending DSO from 45 to 90 days creates an immediate $210,000 liquidity hole. DSCR collapses from 1.35x to 0.38x.",
        )
        self.add_entity(apex_cashflow_squeeze)
        self.add_relation(
            inferred_apex_fragility.node_id,
            RelationType.LEADS_TO_CONSEQUENCE,
            apex_cashflow_squeeze.node_id,
            "Unilateral term extension directly drains working capital cash reserves",
        )

        # Repayment Risk
        apex_risk = GraphNode(
            node_id="RISK_APEX_HIGH_DEFAULT",
            node_type=NodeType.REPAYMENT_RISK,
            label="Severe Default & Illiquidity Risk",
            description="High probability of loan default within 9 months when loan amortization starts.",
        )
        self.add_entity(apex_risk)
        self.add_relation(
            apex_cashflow_squeeze.node_id,
            RelationType.DETERMINES_RISK,
            apex_risk.node_id,
            "Insufficient operating cash flows to service senior bank debt",
        )

        # Underwriting Decision
        decision_apex = GraphNode(
            node_id="DECISION_APEX_REJECT",
            node_type=NodeType.DECISION,
            label="DECISION: REJECT APPLICATION",
            description="Decline loan request despite 742 credit score and 128% paper collateral.",
        )
        self.add_entity(decision_apex)
        self.add_relation(
            apex_risk.node_id,
            RelationType.JUSTIFIES_DECISION,
            decision_apex.node_id,
            "Officer rejects due to unhedged single-customer monopsony and impending liquidity freeze",
        )

        # ====================================================================
        # 2. APPLICATION B: BEACON PRECISION TOOLING (Approved)
        # ====================================================================
        # Stated Baseline Metrics:
        # Credit: 738 | Collateral: $310k | Loan: $250k | Rev: $1.35M | Current DSCR: 1.28x
        beacon = GraphNode(
            node_id="BORROWER_BEACON",
            node_type=NodeType.BORROWER,
            label="Beacon Precision Ltd.",
            description="Precision CNC aerospace & medical components manufacturer requesting $250k expansion loan.",
            metadata={"credit_score": 738, "requested_amount": 250000, "collateral_value": 310000},
        )
        self.add_entity(beacon)

        beacon_credit = GraphNode(
            node_id="FACT_BEACON_CREDIT",
            node_type=NodeType.APPLICATION_FACT,
            label="Prime Credit Score: 738",
            description="Owner credit score 738, one 30-day late utility payment 2 years ago (explained).",
        )
        beacon_collateral = GraphNode(
            node_id="FACT_BEACON_COLLATERAL",
            node_type=NodeType.APPLICATION_FACT,
            label="Collateral: $310,000",
            description="5-Axis DMG Mori CNC machining center with active maintenance records.",
        )
        # The small detail that beginners skim past or perceive negatively
        beacon_recent_cash_dip = GraphNode(
            node_id="FACT_BEACON_TEMPORARY_CASH_DIP",
            node_type=NodeType.APPLICATION_FACT,
            label="Q2 Operating Cash Dip (-$65,000)",
            description="Form detail: Bank statements show a temporary cash contraction in Q2 due to specialized tooling & ISO-13485 audit expenditures.",
        )
        beacon_customer_spread = GraphNode(
            node_id="FACT_BEACON_CLIENT_SPREAD",
            node_type=NodeType.APPLICATION_FACT,
            label="22 Recurring Clients (Max Single = 9%)",
            description="Form detail: Revenue spread across 22 aerospace and medical technology buyers with 3-year recurring contracts.",
        )

        for n in [beacon_credit, beacon_collateral, beacon_recent_cash_dip, beacon_customer_spread]:
            self.add_entity(n)
            self.add_relation(beacon.node_id, RelationType.HAS_FACT, n.node_id, "Form declaration")

        # Officer's Tacit Knowledge
        tacit_iso_moat = GraphNode(
            node_id="TACIT_ISO13485_MOAT",
            node_type=NodeType.TACIT_KNOWLEDGE,
            label="ISO-13485 High Switching-Cost Moat",
            description="Officer's industry expertise: Medical device aerospace audits take 14 months to qualify. Once qualified, clients rarely switch suppliers due to re-certification costs.",
        )
        tacit_dmg_liquidity = GraphNode(
            node_id="TACIT_5AXIS_CNC_LIQUIDITY",
            node_type=NodeType.TACIT_KNOWLEDGE,
            label="5-Axis CNC Global Liquidity",
            description="Officer knows DMG Mori 5-axis machines maintain 85%+ resale value globally; auction resale takes <3 weeks.",
        )
        self.add_entity(tacit_iso_moat)
        self.add_entity(tacit_dmg_liquidity)

        self.add_relation(
            beacon_recent_cash_dip.node_id,
            RelationType.TRIGGERS_TACIT_KNOWLEDGE,
            tacit_iso_moat.node_id,
            "Officer recognizes Q2 cash expense as an essential moat-building capital investment rather than operational bleeding",
        )
        self.add_relation(
            beacon_collateral.node_id,
            RelationType.TRIGGERS_TACIT_KNOWLEDGE,
            tacit_dmg_liquidity.node_id,
            "Officer confirms equipment has ready industrial market resale demand",
        )

        # Inferred Assessments
        inferred_beacon_stickiness = GraphNode(
            node_id="INFER_BEACON_HIGH_STICKINESS",
            node_type=NodeType.INFERRED_ASSESSMENT,
            label="High Customer Retention & Pricing Power",
            description="Diversified customer base with qualified supplier status gives Beacon pricing power and predictable margins.",
        )
        self.add_entity(inferred_beacon_stickiness)
        self.add_relation(
            tacit_iso_moat.node_id,
            RelationType.INFERS,
            inferred_beacon_stickiness.node_id,
            "Certified component status insulates supplier from customer churn",
        )
        self.add_relation(
            beacon_customer_spread.node_id,
            RelationType.INFERS,
            inferred_beacon_stickiness.node_id,
            "Low HHI (Herfindahl index) means loss of any single client impacts <9% of turnover",
        )

        # Financial Consequences
        beacon_cashflow_expansion = GraphNode(
            node_id="CONSEQ_BEACON_RECURRING_CASHFLOW",
            node_type=NodeType.FINANCIAL_CONSEQUENCE,
            label="Contracted Cashflow Expansion & DSCR > 2.1x",
            description="Audit completion unlocks signed purchase orders. Projected DSCR rises to 2.15x over loan term.",
        )
        self.add_entity(beacon_cashflow_expansion)
        self.add_relation(
            inferred_beacon_stickiness.node_id,
            RelationType.LEADS_TO_CONSEQUENCE,
            beacon_cashflow_expansion.node_id,
            "Secured purchase orders translate into high-margin operating cash flows",
        )

        # Repayment Risk
        beacon_risk = GraphNode(
            node_id="RISK_BEACON_LOW_DEFAULT",
            node_type=NodeType.REPAYMENT_RISK,
            label="Robust Debt-Service Capacity (Low Risk)",
            description="Resilient multi-channel cash generation ensures prompt interest and principal repayment.",
        )
        self.add_entity(beacon_risk)
        self.add_relation(
            beacon_cashflow_expansion.node_id,
            RelationType.DETERMINES_RISK,
            beacon_risk.node_id,
            "High forward-looking debt service coverage creates safety buffer",
        )

        # Underwriting Decision
        decision_beacon = GraphNode(
            node_id="DECISION_BEACON_APPROVE",
            node_type=NodeType.DECISION,
            label="DECISION: APPROVE APPLICATION",
            description="Approve $250,000 facility with standard covenant of quarterly financial reviews.",
        )
        self.add_entity(decision_beacon)
        self.add_relation(
            beacon_risk.node_id,
            RelationType.JUSTIFIES_DECISION,
            decision_beacon.node_id,
            "Officer approves based on verified regulatory moat, customer diversification, and strong cash conversion",
        )

        logger.info(
            f"Knowledge Graph created successfully: {self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges."
        )

    def trace_reasoning_path(self, start_node_id: str, end_node_id: str) -> List[List[Dict[str, Any]]]:
        """
        Find all directed reasoning paths from a specific application fact to a final decision.
        Returns detailed multi-hop explanation traces.
        """
        if not nx.has_path(self.graph, start_node_id, end_node_id):
            return []

        all_paths = nx.all_simple_paths(self.graph, start_node_id, end_node_id)
        structured_traces = []

        for path in all_paths:
            path_details = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                u_node = self.nodes_registry[u]
                v_node = self.nodes_registry[v]
                edge_data = self.graph[u][v]
                path_details.append({
                    "from_id": u,
                    "from_type": u_node.node_type.value,
                    "from_label": u_node.label,
                    "relation": edge_data["relation"],
                    "rule": edge_data["rule"],
                    "to_id": v,
                    "to_type": v_node.node_type.value,
                    "to_label": v_node.label,
                })
            structured_traces.append(path_details)

        return structured_traces

    def generate_explanation_report(self) -> str:
        """
        Generates a human-readable comparison report showing the contrast
        between superficial metrics and the deep cognitive reasoning paths.
        """
        apex_paths = self.trace_reasoning_path(
            "FACT_APEX_CLIENT_CONCENTRATION", "DECISION_APEX_REJECT"
        )
        beacon_paths = self.trace_reasoning_path(
            "FACT_BEACON_TEMPORARY_CASH_DIP", "DECISION_BEACON_APPROVE"
        )

        report = []
        report.append("=" * 80)
        report.append("EXECUTIVE UNDERWRITING AUDIT TRAIL: REASONING VS FACTUAL DATA")
        report.append("=" * 80)
        report.append("\n[1] APEX LOGISTICS LTD. (REJECTED)")
        report.append("Superficial Profile: Credit Score 742, Collateral $320k, Current DSCR 1.35x.")
        report.append("Decisive Nuance: 84% revenue concentration with retail giant TitanMart.")
        report.append("\nCognitive Traversal Chain (Why the officer rejected):")

        for p_idx, path in enumerate(apex_paths, 1):
            report.append(f"  Path {p_idx}:")
            for step in path:
                report.append(
                    f"    ({step['from_type']}: {step['from_label']})\n"
                    f"      --[{step['relation']}]--> {step['rule']}\n"
                    f"    ==> ({step['to_type']}: {step['to_label']})\n"
                )

        report.append("-" * 80)
        report.append("[2] BEACON PRECISION LTD. (APPROVED)")
        report.append("Superficial Profile: Credit Score 738, Collateral $310k, Recent Q2 Cash Dip (-$65k).")
        report.append("Decisive Nuance: Q2 cash dip funded ISO-13485 audit; revenue spread across 22 buyers.")
        report.append("\nCognitive Traversal Chain (Why the officer approved):")

        for p_idx, path in enumerate(beacon_paths, 1):
            report.append(f"  Path {p_idx}:")
            for step in path:
                report.append(
                    f"    ({step['from_type']}: {step['from_label']})\n"
                    f"      --[{step['relation']}]--> {step['rule']}\n"
                    f"    ==> ({step['to_type']}: {step['to_label']})\n"
                )

        report.append("=" * 80)
        return "\n".join(report)

    def export_to_json(self, output_path: Path) -> None:
        """Export graph nodes and edges to JSON format."""
        data = {
            "nodes": [node.to_dict() for node in self.nodes_registry.values()],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "relation": data["relation"],
                    "rule": data["rule"],
                    "weight": data["weight"],
                }
                for u, v, data in self.graph.edges(data=True)
            ],
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Graph JSON exported to {output_path}")

    def render_visualization(self, output_image_path: Path) -> None:
        """
        Draws and saves a high-quality visualization of the reasoning knowledge graph.
        Different node categories receive distinct colors and layouts to highlight the
        transition from Facts -> Tacit Knowledge -> Consequences -> Decisions.
        """
        plt.figure(figsize=(18, 12), dpi=300)
        plt.title(
            "Loan Underwriting Knowledge Graph: Modeling Reasoning and Tacit Judgment\n"
            "Comparing Apex Logistics (Rejected) vs Beacon Precision (Approved)",
            fontsize=15,
            fontweight="bold",
            pad=20,
        )

        # Color mapping by NodeType
        color_map = {
            NodeType.BORROWER.value: "#34495E",          # Dark Slate Grey
            NodeType.APPLICATION_FACT.value: "#3498DB",  # Ocean Blue
            NodeType.TACIT_KNOWLEDGE.value: "#E67E22",   # Orange / Intuition
            NodeType.INFERRED_ASSESSMENT.value: "#9B59B6",# Purple / Deduction
            NodeType.FINANCIAL_CONSEQUENCE.value: "#F39C12", # Amber / Cash Impact
            NodeType.REPAYMENT_RISK.value: "#E74C3C",    # Crimson / Risk
            NodeType.DECISION.value: "#2ECC71",          # Emerald / Outcome
        }

        node_colors = [
            color_map.get(self.graph.nodes[n].get("type", ""), "#95A5A6")
            for n in self.graph.nodes()
        ]

        # Use spring layout with tuned k parameter for hierarchical clarity
        pos = nx.spring_layout(self.graph, k=0.9, seed=42, iterations=100)

        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_color=node_colors,
            node_size=3200,
            alpha=0.92,
            edgecolors="#2C3E50",
            linewidths=1.5,
        )

        # Draw edges
        nx.draw_networkx_edges(
            self.graph,
            pos,
            arrows=True,
            arrowstyle="->",
            arrowsize=22,
            edge_color="#7F8C8D",
            width=2.0,
            connectionstyle="arc3,rad=0.08",
        )

        # Draw labels with wrapping
        labels = {}
        for n in self.graph.nodes():
            raw_label = self.graph.nodes[n].get("label", n)
            # Wrap long strings for clean rendering
            words = raw_label.split(" ")
            wrapped = ""
            current_line = ""
            for word in words:
                if len(current_line) + len(word) > 16:
                    wrapped += current_line + "\n"
                    current_line = word + " "
                else:
                    current_line += word + " "
            wrapped += current_line
            labels[n] = wrapped.strip()

        nx.draw_networkx_labels(
            self.graph,
            pos,
            labels=labels,
            font_size=8.5,
            font_family="sans-serif",
            font_weight="bold",
        )

        # Add a custom legend
        legend_handles = [
            plt.Line2D([0], [0], marker="o", color="w", label=nt.value,
                       markerfacecolor=color_map[nt.value], markersize=12)
            for nt in NodeType
        ]
        plt.legend(
            handles=legend_handles,
            title="Knowledge Graph Node Types",
            loc="upper right",
            frameon=True,
            framealpha=0.9,
            facecolor="#F8F9F9",
        )

        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_image_path, dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Visualized graph successfully saved to {output_image_path}")


def main() -> None:
    """Execution entry point."""
    kg = LoanReasoningKnowledgeGraph()
    kg.build_case_studies()

    # Generate and print executive explanation report
    report = kg.generate_explanation_report()
    print(report)

    # Save outputs
    script_dir = Path(__file__).resolve().parent
    output_json = script_dir / "loan_reasoning_graph.json"
    output_img = script_dir / "loan_reasoning_graph.png"
    output_report = script_dir / "reasoning_audit_report.txt"

    kg.export_to_json(output_json)
    kg.render_visualization(output_img)

    with open(output_report, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info(f"Audit report saved to {output_report}")


if __name__ == "__main__":
    main()
