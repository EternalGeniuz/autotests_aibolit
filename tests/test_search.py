import re
from urllib.parse import parse_qs, unquote, urlparse
import pytest
from playwright.sync_api import expect

BASE_URL = "https://mc-aybolit.ru"


def _safe_assert_no_server_error(page):
    txt = page.locator("body").inner_text(timeout=20000).lower()

    error_patterns = [
        r"\binternal server error\b",
        r"\bошибка сервера\b",
        r"\bserver error\b",
        r"\bhttp\s*500\b",
        r"\bошибка\s*500\b",
        r"\berror\s*500\b",
        r"\bкод\s*500\b",
        r"\bstatus\s*500\b",
    ]
    assert not any(re.search(p, txt) for p in error_patterns), "Похоже на страницу ошибки 500"


def _search_input(page):
    # Из HTML: <form action="/search/" ...><input name="q" placeholder="Поиск по сайту">
    return page.locator('form[action="/search/"] input[name="q"]')


def test_g8_h9_01_search_positive_redirects_to_search_page(page):
    page.goto(BASE_URL, wait_until="domcontentloaded")

    search = _search_input(page)
    expect(search).to_be_visible()

    query = "анализ"
    search.fill(query)
    search.press("Enter")

    expect(page).to_have_url(re.compile(r".*/search/\?.*"))
    _safe_assert_no_server_error(page)

    # достаем q из URL и декодируем
    parsed = urlparse(page.url)
    qs = parse_qs(parsed.query)
    assert "q" in qs and qs["q"], f"В URL нет параметра q: {page.url}"

    q_value = unquote(qs["q"][0]).strip().lower()
    assert q_value == query.lower(), f"Ожидали q='{query}', получили q='{q_value}'"


def test_g8_h9_02_clear_search_input(page):
    """
    H9-02 (позитив): очистка поля поиска
    Ожидание: значение инпута очищается.
    """
    page.goto(BASE_URL, wait_until="domcontentloaded")

    search = _search_input(page)
    expect(search).to_be_visible()

    search.fill("узи")
    expect(search).to_have_value("узи")

    search.fill("")
    expect(search).to_have_value("")

    _safe_assert_no_server_error(page)


def test_g8_h9_03_empty_query_submit_no_crash(page):
    """
    H9-03 (негатив): пустой запрос
    Ожидание: нет падения/500. Допускается остаться на главной или перейти на /search/.
    """
    page.goto(BASE_URL, wait_until="domcontentloaded")

    search = _search_input(page)
    expect(search).to_be_visible()

    search.fill("")
    search.press("Enter")

    _safe_assert_no_server_error(page)

    # мягкая проверка: мы либо на главной, либо на /search/
    assert "/search/" in page.url or page.url.rstrip("/") == BASE_URL.rstrip("/")


def test_g8_h9_04_special_chars_query_no_crash(page):
    """
    H9-04 (негатив): спецсимволы
    Ожидание: нет падения/500, открывается /search/ (или остается страница без ошибки).
    """
    page.goto(BASE_URL, wait_until="domcontentloaded")

    search = _search_input(page)
    expect(search).to_be_visible()

    search.fill("!@#$%")
    search.press("Enter")

    _safe_assert_no_server_error(page)
    assert "/search/" in page.url or page.url.startswith(BASE_URL)


def test_g8_h9_05_long_query_300_plus_no_ui_break(page):
    """
    H9-05 (негатив): 300+ символов
    Ожидание: нет падения/500, страница отрабатывает запрос.
    """
    page.goto(BASE_URL, wait_until="domcontentloaded")

    search = _search_input(page)
    expect(search).to_be_visible()

    long_query = "a" * 320
    search.fill(long_query)
    search.press("Enter")

    _safe_assert_no_server_error(page)
    assert "/search/" in page.url or page.url.startswith(BASE_URL)
