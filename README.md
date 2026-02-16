# Analisis-Comp — Competitive Price Auditor for Booking.com

> **Agente de analisis competitivo** que escanea 8 alojamientos en Tigre (Booking.com) en paralelo, extrae precios filtrados por capacidad de huespedes y genera un reporte comparativo con ranking de precios y posicionamiento de tu hotel vs la competencia.

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
  │  │                                        │  │   Tabla comparativa
  │  │  Ranking por precio                    │  │   Posicionamiento
  │  │  Posicion de tu hotel                  │  │   Archivo .txt
  │  │  Diferencia vs mas barato              │  │
  │  └────────────────────────────────────────┘  │
  │     |                                        │
  │     v                                        │
  │    END                                       │
  │                                              │
  └─────────────────────────────────────────────┘
          |
          v
  Output: tabla + reporte + screenshots
```

---

## Hotels Monitored

| # | Hotel | Tipo | Zona |
|---|-------|------|------|
| 1 | **Tigre Centro Cochera Gratis** | TU HOTEL (referencia) | Tigre Centro |
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
| **Reporte en archivo** | Guarda `ultimo_reporte.txt` para referencia |
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
│   └── report.py           Genera tabla comparativa + ranking
│
├── state.py                GraphState, HotelResult, DateScanResult, RoomOption
├── config.py               Lista de hoteles, concurrencia, paths
└── evidencias/             Screenshots por hotel_timestamp (gitignored)
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

## Output Example

Resultado real — 5 sabados, 4 personas, 8 hoteles (40 scrapes en ~2 minutos):

```
==========================================================================================
  ANALISIS COMPETITIVO — Alojamientos Tigre — 4 personas
==========================================================================================

  Fecha: 21/02/2026 -> 22/02/2026
------------------------------------------------------------------------------------------
  Hotel                               Status       Precio 4p          Nota
------------------------------------------------------------------------------------------
  Puerto Delta                        DISPONIBLE   $ 113.812
  Puerto Tigre                        DISPONIBLE   $ 153.480
  Tigre Centro Cochera Gratis         DISPONIBLE   $ 167.433           ** TU HOTEL **
  Hospedaje de la Costa               OCUPADO      —
  Awka Villa del Rio                  OCUPADO      —
  Buenos Aires Rowing Club            OCUPADO      —
  Departamento En Tigre               OCUPADO      —
  La casa de tigre Centro             OCUPADO      —
------------------------------------------------------------------------------------------
  Mas barato: Puerto Delta @ $ 113.812
  Tu hotel esta $ 53,621 MAS CARO que el mas barato

  Fecha: 14/03/2026 -> 15/03/2026
------------------------------------------------------------------------------------------
  Hotel                               Status       Precio 4p          Nota
------------------------------------------------------------------------------------------
  Puerto Delta                        DISPONIBLE   $ 139.527
  Puerto Tigre                        DISPONIBLE   $ 169.903
  Tigre Centro Cochera Gratis         OCUPADO      —                   ** TU HOTEL **
  (... 5 mas ocupados)
------------------------------------------------------------------------------------------
  Mas barato: Puerto Delta @ $ 139.527

==========================================================================================
```

**Insights del analisis real:**

| Fecha | Tu precio | Mas barato | Diferencia | Posicion |
|-------|-----------|------------|------------|----------|
| 21/02 | $167.433 | $113.812 (Puerto Delta) | +$53.621 | 3ro de 3 |
| 28/02 | $167.433 | $113.812 (Puerto Delta) | +$53.621 | 3ro de 4 |
| 07/03 | $167.433 | $113.812 (Puerto Delta) | +$53.621 | 4to de 4 |
| 14/03 | OCUPADO | $139.527 (Puerto Delta) | — | — |
| 21/03 | $167.433 | $130.584 (Puerto Delta) | +$36.849 | 4to de 4 |

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
│   └── report.py           # Tabla comparativa + ranking
├── evidencias/             # Screenshots (gitignored)
├── requirements.txt
├── .gitignore
└── ultimo_reporte.txt      # Ultimo reporte generado (gitignored)
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
- **Built with** Claude Code (Opus 4.6) + RTX 3090 Tech Lab
