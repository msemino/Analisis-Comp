"""Modelos de datos y estado del grafo."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class RoomOption(BaseModel):
    """Una opcion de habitacion con precio y capacidad."""
    guests_max: int
    price_text: str
    price_value: int


class HotelResult(BaseModel):
    """Resultado de la consulta a un hotel individual."""
    slug: str = Field(description="Identificador corto del hotel")
    name: str = Field(description="Nombre del hotel")
    is_own: bool = Field(default=False, description="True si es tu propio hotel")
    status: Literal["AVAILABLE", "OCCUPIED", "CAPTCHA", "ERROR"]
    best_price: str | None = None
    best_price_value: int | None = None
    currency: str = "ARS"
    all_options: list[RoomOption] = Field(default_factory=list)
    matched_options: list[RoomOption] = Field(default_factory=list)
    screenshot_path: str | None = None
    error: str | None = None


class DateScanResult(BaseModel):
    """Resultado de un escaneo de una fecha para todos los hoteles."""
    check_in: str
    check_out: str
    guests: int
    hotels: list[HotelResult] = Field(default_factory=list)


class GraphState(TypedDict, total=False):
    """Estado que fluye entre nodos del grafo."""

    # --- Inputs ---
    dates: list[tuple[str, str]]   # lista de (check_in, check_out) en dd/mm/yyyy
    guests: int

    # --- Outputs ---
    scan_results: list[DateScanResult]
