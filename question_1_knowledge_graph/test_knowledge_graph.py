"""
Unit Tests for Loan Reasoning Knowledge Graph
==============================================
Tests verify:
1. Graph topological integrity and non-emptiness.
2. Distinct multi-layer node typing across facts, tacit knowledge, and decisions.
3. Existence of complete, unbroken reasoning paths from decisive application facts to decisions.
4. Correctness of underwriting outcome mapping (Apex -> Reject, Beacon -> Approve).
"""

import pytest
from pathlib import Path
from loan_reasoning_graph import (
    LoanReasoningKnowledgeGraph,
    NodeType,
    RelationType,
)


@pytest.fixture
def populated_kg() -> LoanReasoningKnowledgeGraph:
    """Fixture returning a pre-built knowledge graph."""
    kg = LoanReasoningKnowledgeGraph()
    kg.build_case_studies()
    return kg


def test_graph_has_nodes_and_edges(populated_kg: LoanReasoningKnowledgeGraph):
    """Verify that graph contains expected entities and relationships."""
    assert populated_kg.graph.number_of_nodes() >= 20
    assert populated_kg.graph.number_of_edges() >= 20


def test_all_node_types_represented(populated_kg: LoanReasoningKnowledgeGraph):
    """Verify that all cognitive layers defined in NodeType are present in the graph."""
    present_types = {
        data["type"] for _, data in populated_kg.graph.nodes(data=True)
    }
    for expected_type in NodeType:
        assert expected_type.value in present_types, f"Missing layer: {expected_type.value}"


def test_apex_rejection_reasoning_chain(populated_kg: LoanReasoningKnowledgeGraph):
    """
    Ensure an unbroken directed path exists from Apex's client concentration
    fact to the final REJECT decision.
    """
    paths = populated_kg.trace_reasoning_path(
        "FACT_APEX_CLIENT_CONCENTRATION", "DECISION_APEX_REJECT"
    )
    assert len(paths) >= 1, "No reasoning path found from fact to rejection!"

    # Verify that the path traverses tacit knowledge and financial consequence
    first_path = paths[0]
    types_in_path = [step["to_type"] for step in first_path]

    assert NodeType.TACIT_KNOWLEDGE.value in types_in_path
    assert NodeType.INFERRED_ASSESSMENT.value in types_in_path
    assert NodeType.FINANCIAL_CONSEQUENCE.value in types_in_path
    assert NodeType.REPAYMENT_RISK.value in types_in_path
    assert NodeType.DECISION.value in types_in_path


def test_beacon_approval_reasoning_chain(populated_kg: LoanReasoningKnowledgeGraph):
    """
    Ensure an unbroken directed path exists from Beacon's temporary cash dip
    to the final APPROVAL decision.
    """
    paths = populated_kg.trace_reasoning_path(
        "FACT_BEACON_TEMPORARY_CASH_DIP", "DECISION_BEACON_APPROVE"
    )
    assert len(paths) >= 1, "No reasoning path found from fact to approval!"

    first_path = paths[0]
    types_in_path = [step["to_type"] for step in first_path]

    assert NodeType.TACIT_KNOWLEDGE.value in types_in_path
    assert NodeType.FINANCIAL_CONSEQUENCE.value in types_in_path
    assert NodeType.DECISION.value in types_in_path


def test_export_json_validity(populated_kg: LoanReasoningKnowledgeGraph, tmp_path: Path):
    """Verify JSON export creates a valid readable file."""
    export_file = tmp_path / "test_export.json"
    populated_kg.export_to_json(export_file)
    assert export_file.exists()
    assert export_file.stat().st_size > 500
