"""Nodo reporte: genera tabla comparativa por consola y archivo."""

from __future__ import annotations

from config import PROJECT_DIR
from state import GraphState, DateScanResult


async def report_node(state: GraphState) -> GraphState:
    """Nodo LangGraph: imprime y guarda reporte comparativo."""

    results = state.get("scan_results", [])
    guests = state.get("guests", 4)

    lines: list[str] = []
    lines.append("=" * 90)
    lines.append(f"  ANALISIS COMPETITIVO — Alojamientos Tigre — {guests} personas")
    lines.append("=" * 90)

    for scan in results:
        lines.append("")
        lines.append(f"  Fecha: {scan.check_in} -> {scan.check_out}")
        lines.append("-" * 90)
        lines.append(
            f"  {'Hotel':<35} {'Status':<12} {'Precio '+ str(guests) + 'p':<18} {'Nota'}"
        )
        lines.append("-" * 90)

        # Ordenar: disponibles por precio, luego ocupados, luego errores
        available = [h for h in scan.hotels if h.status == "AVAILABLE" and h.best_price_value]
        occupied = [h for h in scan.hotels if h.status == "OCCUPIED"]
        others = [h for h in scan.hotels if h.status not in ("AVAILABLE", "OCCUPIED") or (h.status == "AVAILABLE" and not h.best_price_value)]

        available.sort(key=lambda h: h.best_price_value or 999999999)

        for h in available:
            tag = " ** TU HOTEL **" if h.is_own else ""
            note = ""
            if h.error:
                note = h.error
            elif not h.matched_options:
                note = "precio gral (sin opcion p/ " + str(guests) + ")"
            lines.append(
                f"  {h.name:<35} {'DISPONIBLE':<12} {h.best_price or '-':<18} {note}{tag}"
            )

        for h in occupied:
            tag = " ** TU HOTEL **" if h.is_own else ""
            lines.append(
                f"  {h.name:<35} {'OCUPADO':<12} {'—':<18} {tag}"
            )

        for h in others:
            tag = " ** TU HOTEL **" if h.is_own else ""
            lines.append(
                f"  {h.name:<35} {h.status:<12} {'—':<18} {h.error or ''}{tag}"
            )

        lines.append("-" * 90)

        # Resumen rapido
        if available:
            cheapest = available[0]
            own = next((h for h in scan.hotels if h.is_own), None)
            lines.append(f"  Mas barato: {cheapest.name} @ {cheapest.best_price}")
            if own and own.best_price_value and cheapest.best_price_value:
                diff = own.best_price_value - cheapest.best_price_value
                if diff > 0:
                    lines.append(f"  Tu hotel esta $ {diff:,} MAS CARO que el mas barato")
                elif diff < 0:
                    lines.append(f"  Tu hotel es EL MAS BARATO ($ {abs(diff):,} menos)")
                else:
                    lines.append(f"  Tu hotel IGUALA al mas barato")

    lines.append("")
    lines.append("=" * 90)

    report_text = "\n".join(lines)

    # Imprimir
    print(report_text)

    # Guardar archivo
    report_path = PROJECT_DIR / "ultimo_reporte.txt"
    report_path.write_text(report_text, encoding="utf-8")

    return state
