"""Nodo reporte: serializa resultados a JSON + texto para retrieve."""

from __future__ import annotations

import json
from datetime import datetime

from config import PROJECT_DIR
from state import GraphState


def _build_text_report(output: dict) -> str:
    """Genera reporte en texto plano legible para retrieve/consultas."""
    lines: list[str] = []
    sep = "=" * 90
    subsep = "-" * 90

    lines.append(sep)
    lines.append(f"  ANALISIS COMPETITIVO — Alojamientos Tigre — {output['guests']} personas")
    lines.append(f"  Generado: {output['generated_at']}")
    lines.append(sep)

    for scan in output["scans"]:
        lines.append("")
        lines.append(f"  Fecha: {scan['check_in']} -> {scan['check_out']}")
        lines.append(subsep)
        lines.append(f"  {'Hotel':<36} {'Status':<13} {'Precio':<18} {'Opciones':<10} {'Nota'}")
        lines.append(subsep)

        # Ordenar: disponibles primero (por precio), luego ocupados
        available = [h for h in scan["hotels"] if h["status"] == "AVAILABLE"]
        others = [h for h in scan["hotels"] if h["status"] != "AVAILABLE"]
        available.sort(key=lambda h: h.get("best_price_value") or 999_999_999)

        for h in available + others:
            name = h["name"][:35]
            status = h["status"]

            if status == "AVAILABLE" and h.get("best_price"):
                precio = h["best_price"]
            else:
                precio = "—"

            n_matched = len(h.get("matched_options", []))
            n_all = len(h.get("all_options", []))
            opciones = f"{n_matched}/{n_all}"

            nota = ""
            if h.get("is_own"):
                nota = "** TU HOTEL **"
            if h.get("error"):
                nota += f" [{h['error'][:30]}]"

            lines.append(f"  {name:<36} {status:<13} {precio:<18} {opciones:<10} {nota}")

            # Detalle de opciones matched
            for opt in h.get("matched_options", []):
                lines.append(f"    └─ {opt['guests_max']}p: {opt['price_text']}")

        lines.append(subsep)

        # Resumen de la fecha
        if available:
            cheapest = available[0]
            lines.append(f"  Mas barato: {cheapest['name']} @ {cheapest.get('best_price', '?')}")

            own = [h for h in available if h.get("is_own")]
            if own and own[0].get("best_price_value") and cheapest.get("best_price_value"):
                diff = own[0]["best_price_value"] - cheapest["best_price_value"]
                if diff > 0:
                    lines.append(f"  Tu hotel esta $ {diff:,} MAS CARO que el mas barato")
                elif diff < 0:
                    lines.append(f"  Tu hotel esta $ {abs(diff):,} MAS BARATO que el siguiente")
                else:
                    lines.append(f"  Tu hotel ES el mas barato")
            elif own and own[0].get("status") != "AVAILABLE":
                lines.append(f"  Tu hotel: OCUPADO / SIN DISPONIBILIDAD")
        else:
            lines.append(f"  Sin hoteles disponibles para esta fecha")

    lines.append("")
    lines.append(sep)
    lines.append(f"  Total: {output['dates_scanned']} fecha(s), {output['hotels_per_date']} hoteles por fecha")
    lines.append(sep)

    return "\n".join(lines)


async def report_node(state: GraphState) -> GraphState:
    """Nodo LangGraph: exporta resultados a JSON + texto."""

    results = state.get("scan_results", [])
    guests = state.get("guests", 4)

    # --- Construir dict estructurado ---
    output = {
        "generated_at": datetime.now().isoformat(),
        "guests": guests,
        "dates_scanned": len(results),
        "hotels_per_date": len(results[0].hotels) if results else 0,
        "scans": [],
    }

    for scan in results:
        date_entry = {
            "check_in": scan.check_in,
            "check_out": scan.check_out,
            "hotels": [],
        }
        for h in scan.hotels:
            hotel_entry = {
                "slug": h.slug,
                "name": h.name,
                "is_own": h.is_own,
                "status": h.status,
                "best_price": h.best_price,
                "best_price_value": h.best_price_value,
                "currency": h.currency,
                "matched_options": [
                    {"guests_max": o.guests_max, "price_text": o.price_text, "price_value": o.price_value}
                    for o in h.matched_options
                ],
                "all_options": [
                    {"guests_max": o.guests_max, "price_text": o.price_text, "price_value": o.price_value}
                    for o in h.all_options
                ],
            }
            if h.error:
                hotel_entry["error"] = h.error
            date_entry["hotels"].append(hotel_entry)
        output["scans"].append(date_entry)

    # --- Guardar JSON ---
    json_str = json.dumps(output, indent=2, ensure_ascii=False)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = PROJECT_DIR / f"scan_{ts}.json"
    json_path.write_text(json_str, encoding="utf-8")

    # --- Guardar reporte texto (para retrieve / consultas) ---
    reportes_dir = PROJECT_DIR / "reportes"
    reportes_dir.mkdir(exist_ok=True)

    text_report = _build_text_report(output)
    txt_path = reportes_dir / f"reporte_{ts}.txt"
    txt_path.write_text(text_report, encoding="utf-8")

    # --- Imprimir a consola ---
    print(text_report)
    print()
    print(json_str)
    print()
    print(f"[+] JSON guardado: {json_path}")
    print(f"[+] Reporte texto: {txt_path}")

    return state
