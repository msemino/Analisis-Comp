"""Grafo LangGraph del analisis competitivo.

    START -> scan_all_dates -> report -> END
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from state import GraphState
from nodes import scan_all_dates_node, report_node


def build_graph() -> StateGraph:
    builder = StateGraph(GraphState)

    builder.add_node("scan_all_dates", scan_all_dates_node)
    builder.add_node("report", report_node)

    builder.add_edge(START, "scan_all_dates")
    builder.add_edge("scan_all_dates", "report")
    builder.add_edge("report", END)

    return builder.compile()
