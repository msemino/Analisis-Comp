"""Entry point — Analisis Competitivo de Alojamientos en Tigre.

Uso:
    python main.py 21/02/2026 28/02/2026 07/03/2026          # varias fechas, 4 personas
    python main.py 21/02/2026 --guests 2                      # una fecha, 2 personas
    python main.py 21/02/2026 28/02/2026 --guests 6           # varias fechas, 6 personas

Cada fecha es un check-in de 1 noche (checkout = dia siguiente automatico).
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from graph import build_graph


def _next_day(date_str: str) -> str:
    """Dado dd/mm/yyyy devuelve el dia siguiente en mismo formato."""
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    return (dt + timedelta(days=1)).strftime("%d/%m/%Y")


async def run(dates: list[str], guests: int) -> None:
    graph = build_graph()

    date_pairs = [(d, _next_day(d)) for d in dates]

    print(f"[*] Analisis Competitivo — {len(date_pairs)} fecha(s), {guests} personas")
    print(f"[*] Hoteles: 8 (1 propio + 7 competidores)")
    print(f"[*] Fechas: {', '.join(dates)}")
    print()

    await graph.ainvoke({
        "dates": date_pairs,
        "guests": guests,
    })


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analisis Competitivo de Alojamientos en Tigre",
    )
    parser.add_argument(
        "dates", nargs="+", type=str,
        help="Fechas de check-in (dd/mm/yyyy). Checkout = dia siguiente.",
    )
    parser.add_argument(
        "--guests", type=int, default=4,
        help="Cantidad de huespedes (default: 4)",
    )
    args = parser.parse_args()

    asyncio.run(run(args.dates, args.guests))


if __name__ == "__main__":
    main()
