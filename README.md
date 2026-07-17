# Analisis-Comp — Competitive Price Auditor for Booking.com

> **Agente de analisis competitivo** que escanea 8 alojamientos en Tigre (Booking.com) en paralelo, extrae precios filtrados por capacidad de huespedes y genera doble output: **JSON estructurado** (para integracion con otros agentes) + **reporte texto** (para retrieve y consultas historicas).

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.58-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-orange?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)

---

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Hotels Monitored](#hotels-monitored)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Output Example](#output-example)
- [Project Structure](#project-structure)
- [Extending](#extending)
- [Performance](#performance)
- [Related Projects](#related-projects)
- [Credits](#credits)

---

## Overview

Analisis-Comp nace de una necesidad real: saber como se posiciona tu alojamiento en precio y disponibilidad respecto a la competencia directa en Booking.com, para fechas especificas (tipicamente fines de semana).

**Problema:** Revisar manualmente 8 hoteles x N fechas en Booking.com es tedioso y propenso a errores.

**Solucion:** Un agente que en ~20 segundos escanea los 8 hoteles en paralelo para una fecha, extrae precios filtrados por capacidad, y te dice exactamente donde estas parado.

---

## How It Works

```
  Input: fechas[] + huespedes
          |
          v
  ┌─────────────────────────────────────────────┐
  │             LangGraph Engine                 │
  │                                              │
  │   START                                      │
  │     |                                        │
  │     v                                        │
  │  ┌────────────────────────────────────────┐  │
  │  │         scan_all_dates                 │  │
  │  │                                        │  │
  │  │  Para cada fecha:                      │  │
  │  │    ┌─────────┐  ┌─────────┐            │  │
  │  │    │ Hotel 1 │  │ Hotel 2 │  ...x8     │  │   Playwright paralelo
  │  │    │Playwright│  │Playwright│  (4 conc) │  │   CSS selectors
  │  │    └─────────┘  └─────────┘            │  │   Filtro por capacidad
  │  └────────────────────────────────────────┘  │
  │     |                                        │
  │     v                                        │
  │  ┌────────────────────────────────────────┐  │
  │  │           report                       │  │
  │  │                                        │  │   JSON estructurado
  │  │  scan_{ts}.json (integracion)         │  │   Reporte texto
  │  │  reportes/reporte_{ts}.txt (retrieve) │  │   Screenshots
  │  │  Ranking + posicionamiento            │  │
  │  └────────────────────────────────────────┘  │
  │     |                                        │
  │     v                                        │
  │    END                                       │
  │                                              │
  └─────────────────────────────────────────────┘
          |
          v
  Output: JSON + texto + screenshots
```

---

## Hotels Monitored

| # | Hotel | Tipo | Zona |
|---|-------|------|------|
| 1 | **Mi propiedad (ejemplo)** | TU HOTEL (referencia) | Tigre Centro |
| 2 | Puerto Delta | Competidor | Delta |
| 3 | Puerto Tigre | Competidor | Tigre |
| 4 | Hospedaje de la Costa | Competidor | Tigre |
| 5 | Awka Villa del Rio | Competidor | Tigre |
| 6 | Buenos Aires Rowing Club | Competidor | Tigre |
| 7 | Departamento En Tigre | Competidor | Tigre |
| 8 | La casa de tigre Centro | Competidor | Tigre Centro |

Para agregar o cambiar hoteles, editar la lista `HOTELS` en `config.py`.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Escaneo paralelo** | 4 browsers simultaneos (configurable), ~20 seg por fecha |
| **Multi-fecha** | N fechas en un solo comando |
| **Filtrado por capacidad** | Precio real para la cantidad de huespedes solicitada |
| **Ranking automatico** | Hoteles ordenados por precio, mas barato primero |
| **Posicionamiento** | Te dice cuanto mas caro/barato estas vs la competencia |
| **Deteccion de estados** | AVAILABLE, OCCUPIED, CAPTCHA, ERROR por hotel |
| **Evidencia visual** | Screenshot por hotel/fecha en `evidencias/` |
| **JSON estructurado** | `scan_{ts}.json` con todos los datos para integracion downstream |
| **Reportes texto** | `reportes/reporte_{ts}.txt` acumulativos para retrieve/consultas |
| **Zero LLM** | Playwright directo, sin API keys, sin costo, sin VRAM |

---

## Architecture

```
Analisis-Comp/
│
├── main.py                 CLI: recibe fechas + guests, invoca grafo
│     |
│     v
├── graph.py                LangGraph: scan_all_dates -> report -> END
│     |
│     v
├── nodes/
│   ├── scraper.py          Playwright paralelo: 8 hoteles x N fechas
│   └── report.py           JSON + texto para retrieve
│
├── state.py                GraphState, HotelResult, DateScanResult, RoomOption
├── config.py               Lista de hoteles, concurrencia, paths
├── evidencias/             Screenshots por hotel_timestamp (gitignored)
└── reportes/               Reportes .txt acumulativos (gitignored)
```

**Modelos de datos:**

```
GraphState
  ├── dates: [(check_in, check_out), ...]
  ├── guests: int
  └── scan_results: [DateScanResult]
                       ├── check_in, check_out, guests
                       └── hotels: [HotelResult]
                                     ├── slug, name, is_own
                                     ├── status: AVAILABLE|OCCUPIED|CAPTCHA|ERROR
                                     ├── best_price, best_price_value
                                     ├── currency
                                     ├── all_options: [RoomOption]
                                     ├── matched_options: [RoomOption]
                                     └── screenshot_path
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Scraping** | Playwright 1.58 | Browser automation paralelo |
| **Orchestration** | LangGraph 1.0 | Grafo de estados extensible |
| **Data Models** | Pydantic 2.x | Validacion tipada de resultados |
| **Concurrency** | asyncio.Semaphore | Control de paralelismo (4 browsers max) |
| **Parsing** | CSS Selectors | Extraccion determinista del DOM |

---

## Getting Started

### Prerequisites

- **Python 3.11+** (3.14 testeado)
- **Playwright Chromium**

### Installation

```bash
git clone https://github.com/msemino/Analisis-Comp.git
cd Analisis-Comp

pip install -r requirements.txt
python -m playwright install chromium
```

---

## Usage

### Una fecha, 4 personas (default)

```bash
python main.py 21/02/2026
```

### Multiples fechas

```bash
python main.py 21/02/2026 28/02/2026 07/03/2026 14/03/2026 21/03/2026
```

### Cambiar cantidad de huespedes

```bash
python main.py 21/02/2026 --guests 2
```

### Scan de 5 sabados para 4 personas

```bash
python main.py 21/02/2026 28/02/2026 07/03/2026 14/03/2026 21/03/2026 --guests 4
```

**Cada fecha es un check-in de 1 noche** (checkout = dia siguiente automatico).

---

## Output

Cada ejecucion genera **dos archivos**:

| Archivo | Formato | Uso |
|---------|---------|-----|
| `scan_{timestamp}.json` | JSON estructurado | Integracion con otros agentes/sistemas |
| `reportes/reporte_{timestamp}.txt` | Texto plano | Retrieve, consultas historicas, RAG |

Los reportes texto se acumulan en `reportes/` — cada ejecucion agrega uno nuevo, nunca sobreescribe.

### JSON Output (para integracion)

```json
{
  "generated_at": "2026-02-16T...",
  "guests": 4,
  "dates_scanned": 2,
  "hotels_per_date": 8,
  "scans": [
    {
      "check_in": "21/02/2026",
      "check_out": "22/02/2026",
      "hotels": [
        {
          "slug": "mi-propiedad",
          "name": "Mi propiedad (ejemplo)",
          "is_own": true,
          "status": "AVAILABLE",
          "best_price": "$ 167.433",
          "best_price_value": 167433,
          "currency": "ARS",
          "matched_options": [
            {"guests_max": 4, "price_text": "$ 167.433", "price_value": 167433}
          ],
          "all_options": [
            {"guests_max": 1, "price_text": "$ 142.318", "price_value": 142318},
            {"guests_max": 4, "price_text": "$ 167.433", "price_value": 167433}
          ]
        }
      ]
    }
  ]
}
```

### Reporte Texto (para retrieve)

```
==========================================================================================
  ANALISIS COMPETITIVO — Alojamientos Tigre — 4 personas
  Generado: 2026-02-16T...
==========================================================================================

  Fecha: 21/02/2026 -> 22/02/2026
------------------------------------------------------------------------------------------
  Hotel                                Status        Precio             Opciones   Nota
------------------------------------------------------------------------------------------
  Puerto Delta                         AVAILABLE     $ 113.812          1/3
    └─ 4p: $ 113.812
  Puerto Tigre                         AVAILABLE     $ 153.480          1/4
    └─ 4p: $ 153.480
  Mi propiedad (ejemplo)               AVAILABLE     $ 167.433          1/2        ** TU HOTEL **
    └─ 4p: $ 167.433
  Hospedaje de la Costa                OCCUPIED      —                  0/0
  Awka Villa del Rio                   OCCUPIED      —                  0/0
  Buenos Aires Rowing Club             OCCUPIED      —                  0/0
------------------------------------------------------------------------------------------
  Mas barato: Puerto Delta @ $ 113.812
  Tu hotel esta $ 53,621 MAS CARO que el mas barato

==========================================================================================
  Total: 1 fecha(s), 8 hoteles por fecha
==========================================================================================
```

---

## Project Structure

```
Analisis-Comp/
├── main.py                 # CLI multi-fecha
├── graph.py                # LangGraph: scan -> report -> END
├── state.py                # GraphState + HotelResult + RoomOption
├── config.py               # 8 hoteles + settings
├── nodes/
│   ├── __init__.py
│   ├── scraper.py          # Playwright paralelo (core)
│   └── report.py           # JSON + texto para retrieve
├── evidencias/             # Screenshots (gitignored)
├── reportes/               # Reportes .txt acumulativos (gitignored)
│   ├── reporte_20260216_143022.txt
│   └── reporte_20260216_150511.txt
├── scan_*.json             # JSON estructurado (gitignored)
├── requirements.txt
└── .gitignore
```

---

## Extending

### Agregar un hotel

Editar `config.py`:

```python
HOTELS = [
    # ... existentes ...
    ("nuevo-hotel", "Nombre Hotel", "https://www.booking.com/hotel/ar/slug.es-ar.html", False),
]
```

### Agregar un nodo al grafo

```python
# graph.py
builder.add_node("alert", alert_node)
builder.add_edge("report", "alert")
builder.add_edge("alert", END)
```

### Ideas de nodos futuros

| Nodo | Funcion |
|------|---------|
| `price_history` | Guardar historico en SQLite, detectar tendencias |
| `telegram_alert` | Notificar cuando un competidor baja precio |
| `csv_export` | Exportar resultados a CSV/Excel |
| `dashboard` | Web UI con graficos de precios historicos |
| `auto_schedule` | Cron job que corre automaticamente cada semana |

---

## Performance

| Metric | Value |
|--------|-------|
| 1 fecha x 8 hoteles | ~20 segundos |
| 5 fechas x 8 hoteles (40 scrapes) | ~2 minutos |
| Concurrencia | 4 browsers simultaneos |
| VRAM | 0 (sin LLM) |
| Costo | $0 (sin API keys) |
| Fiabilidad | Determinista (CSS selectors, no LLM) |

---

## Related Projects

| Proyecto | Descripcion |
|----------|-------------|
| [agente-book](https://github.com/msemino/agente-book) | Scraper individual de un hotel — precursor de este proyecto |
| [agent-lightning](https://github.com/microsoft/agent-lightning) | Framework de Microsoft para RL/APO sobre agentes LangGraph |

---

## Credits

- **Playwright** — [playwright.dev](https://playwright.dev)
- **LangGraph** — [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- **Pydantic** — [pydantic.dev](https://docs.pydantic.dev)
- **Built with** Claude Code (Opus 4.6) + 24 GB GPU Tech Lab
