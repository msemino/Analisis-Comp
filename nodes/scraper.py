"""Nodo scraper: consulta todos los hoteles en paralelo para cada fecha."""

from __future__ import annotations

import asyncio
import re
from datetime import datetime

from playwright.async_api import async_playwright, Browser, BrowserContext

from config import EVIDENCIAS_DIR, HEADLESS, HOTELS, MAX_CONCURRENT
from state import DateScanResult, GraphState, HotelResult, RoomOption

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


async def scan_all_dates_node(state: GraphState) -> GraphState:
    """Nodo LangGraph: para cada fecha, escanea todos los hoteles en paralelo."""

    dates = state["dates"]
    guests = state.get("guests", 4)
    all_results: list[DateScanResult] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)

        for check_in, check_out in dates:
            scan = await _scan_one_date(browser, check_in, check_out, guests)
            all_results.append(scan)

        await browser.close()

    return {"scan_results": all_results}


async def _scan_one_date(
    browser: Browser,
    check_in: str,
    check_out: str,
    guests: int,
) -> DateScanResult:
    """Escanea todos los hoteles para una fecha, con concurrencia limitada."""

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def _scrape_with_limit(slug, name, url, is_own):
        async with semaphore:
            return await _scrape_hotel(browser, slug, name, url, is_own, check_in, check_out, guests)

    tasks = [
        _scrape_with_limit(slug, name, url, is_own)
        for slug, name, url, is_own in HOTELS
    ]
    hotels = await asyncio.gather(*tasks)

    return DateScanResult(
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        hotels=list(hotels),
    )


async def _scrape_hotel(
    browser: Browser,
    slug: str,
    name: str,
    base_url: str,
    is_own: bool,
    check_in: str,
    check_out: str,
    guests: int,
) -> HotelResult:
    """Scrape un hotel individual con Playwright directo."""

    cin = datetime.strptime(check_in, "%d/%m/%Y").strftime("%Y-%m-%d")
    cout = datetime.strptime(check_out, "%d/%m/%Y").strftime("%Y-%m-%d")
    target_url = f"{base_url}?checkin={cin}&checkout={cout}&group_adults={guests}&no_rooms=1"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    ctx = await browser.new_context(
        user_agent=_UA,
        viewport={"width": 1366, "height": 768},
        locale="es-AR",
    )
    page = await ctx.new_page()

    try:
        await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(6000)

        body_text = await page.text_content("body") or ""

        # --- CAPTCHA ---
        if "captcha" in body_text.lower() or await page.query_selector("[id*=captcha]"):
            img = EVIDENCIAS_DIR / f"{slug}_{ts}.png"
            await page.screenshot(path=str(img))
            return HotelResult(
                slug=slug, name=name, is_own=is_own,
                status="CAPTCHA", screenshot_path=str(img),
            )

        # --- No disponible ---
        if "no tenemos disponibilidad" in body_text.lower():
            img = EVIDENCIAS_DIR / f"{slug}_{ts}.png"
            await page.screenshot(path=str(img))
            return HotelResult(
                slug=slug, name=name, is_own=is_own,
                status="OCCUPIED", screenshot_path=str(img),
            )

        # --- Extraer precios por fila ---
        rows = await page.query_selector_all(
            "#hprt-table tr.js-rt-block-row, #hprt-table tr[data-block-id]"
        )

        all_options: list[RoomOption] = []
        for row in rows:
            # Capacidad
            icons = await row.query_selector_all(
                ".hprt-occupancy-occupancy-info svg, .hprt-occupancy-occupancy-info i"
            )
            guests_max = len(icons) if icons else 0
            if guests_max == 0:
                occ = await row.query_selector("td.hprt-table-cell-occupancy")
                if occ:
                    m = re.search(r"(\d+)", await occ.text_content() or "")
                    if m:
                        guests_max = int(m.group(1))

            # Precio
            span = await row.query_selector("span.prco-valign-middle-helper")
            if not span:
                continue
            price_text = (await span.text_content() or "").strip()
            if not price_text:
                continue

            price_value = _parse_price(price_text)
            all_options.append(RoomOption(
                guests_max=guests_max, price_text=price_text, price_value=price_value,
            ))

        # Screenshot
        img = EVIDENCIAS_DIR / f"{slug}_{ts}.png"
        table = await page.query_selector("#hprt-table")
        if table:
            await table.scroll_into_view_if_needed()
            await page.wait_for_timeout(300)
        await page.screenshot(path=str(img))

        if not all_options:
            return HotelResult(
                slug=slug, name=name, is_own=is_own,
                status="ERROR", error="Tabla de precios vacia",
                screenshot_path=str(img),
            )

        matched = [o for o in all_options if o.guests_max >= guests]
        first = all_options[0].price_text
        currency = "USD" if ("USD" in first or "US$" in first) else "ARS"

        if matched:
            best = min(matched, key=lambda o: o.price_value)
            return HotelResult(
                slug=slug, name=name, is_own=is_own,
                status="AVAILABLE",
                best_price=best.price_text,
                best_price_value=best.price_value,
                currency=currency,
                all_options=all_options,
                matched_options=matched,
                screenshot_path=str(img),
            )
        else:
            best_any = min(all_options, key=lambda o: o.price_value)
            return HotelResult(
                slug=slug, name=name, is_own=is_own,
                status="AVAILABLE",
                best_price=best_any.price_text,
                best_price_value=best_any.price_value,
                currency=currency,
                all_options=all_options,
                matched_options=[],
                screenshot_path=str(img),
                error=f"Sin opciones para {guests} pers. Max: {max(o.guests_max for o in all_options)}",
            )

    except Exception as exc:
        return HotelResult(
            slug=slug, name=name, is_own=is_own,
            status="ERROR", error=f"{type(exc).__name__}: {exc}",
        )
    finally:
        await ctx.close()


def _parse_price(text: str) -> int:
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0
