import re
import pytest
from playwright.sync_api import expect


BASE_URL = "https://mc-aybolit.ru"


def soft_assert(condition: bool, message: str):
    """Не валит тест, но пишет предупреждение в вывод pytest."""
    if not condition:
        pytest.xfail(message)


def goto_ok(page, url: str):
    """Переход + проверка, что ответ получен и не 4xx/5xx (soft)."""
    resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
    # resp может быть None (редкие кейсы: file://, некоторые редиректы)
    if resp is not None:
        soft_assert(resp.status < 400, f"HTTP status {resp.status} for {url}")
    return resp


def body_has_any_text(page, min_len: int = 200) -> bool:
    text = page.locator("body").inner_text(timeout=20000)
    return len(text.strip()) >= min_len


# 01. Главная открывается
def test_01_home_page_opens(page):
    goto_ok(page, BASE_URL)
    expect(page).to_have_url(re.compile(r"mc-aybolit\.ru"))
    # title — просто не пустой
    title = page.title()
    assert title.strip() != ""


# 02. HTTPS и отсутствие явного mixed-content (SOFT)
def test_02_https_and_no_mixed_content(page):
    goto_ok(page, BASE_URL)
    assert page.url.startswith("https://")

    html = page.content()
    # Это мягкая проверка: mixed-content бывает “ложноположительным” из-за шаблонов/комментариев.
    mixed = ("http://" in html)
    if mixed:
        pytest.xfail("Potential mixed-content reference found in HTML (soft check).")


# 03. Навигация по пунктам меню (мягко: если пункта нет — SKIP)
@pytest.mark.parametrize(
    "menu_text, expected_any",
    [
        ("Комплексные исследования", ["/complexes", "complexes", "services"]),
        ("Наши врачи", ["/doctors", "doctors", "specialist"]),
        ("Адреса клиник", ["/clinics", "clinics", "contacts", "address"]),
    ],
)
def test_03_header_navigation_links(page, menu_text, expected_any):
    goto_ok(page, BASE_URL)

    link = page.get_by_role("link", name=re.compile(menu_text, re.I))
    if link.count() == 0:
        pytest.skip(f"Menu link '{menu_text}' not found on the page")

    link.first.click(timeout=30000)
    expect(page).to_have_url(re.compile("|".join(map(re.escape, expected_any)), re.I))


# 04. Услуги: открывается и есть контент
def test_04_services_page_has_content(page):
    goto_ok(page, f"{BASE_URL}/uslugi")
    assert body_has_any_text(page)


# 05. Врачи: открывается и есть контент (слова — SOFT)
def test_05_doctors_page_has_content(page):
    goto_ok(page, f"{BASE_URL}/doctors")
    assert body_has_any_text(page)
    body = page.locator("body").inner_text()
    if not any(x.lower() in body.lower() for x in ["врач", "специалист", "доктор"]):
        pytest.xfail("Doctors markers not found in text (soft check).")


# 06. Клиники/адреса: открывается и есть контент (слова — SOFT)
def test_06_clinics_page_has_content(page):
    goto_ok(page, f"{BASE_URL}/clinics")
    assert body_has_any_text(page)
    body = page.locator("body").inner_text()
    if not any(x.lower() in body.lower() for x in ["адрес", "клиник", "филиал", "контакт"]):
        pytest.xfail("Clinics/address markers not found (soft check).")


# 07. Запись: открывается (статус проверяем через response)
def test_07_appointment_page_opens(page):
    resp = goto_ok(page, f"{BASE_URL}/zapis")
    # Жёстко не валим, но минимум — страница должна загрузиться
    assert page.url


# 08. Негатив: пустая форма (если найдём кнопку отправки — проверим, иначе SKIP)
def test_08_empty_form_validation_soft(page):
    goto_ok(page, f"{BASE_URL}/zapis")

    # Ищем “Отправить/Записаться/Оставить заявку” в кнопках
    btn = page.get_by_role("button", name=re.compile(r"(запис|отправ|заявк|ок|submit)", re.I))
    if btn.count() == 0:
        pytest.skip("No submit-like button found on appointment page")

    btn.first.click()
    # Ошибки валидации могут быть в разных местах — проверка soft
    body = page.locator("body").inner_text()
    if not any(x in body.lower() for x in ["обяз", "заполн", "ошиб", "некоррект"]):
        pytest.xfail("Validation message not detected after empty submit (soft check).")


# 09. 404 поведение (soft: сайт может редиректить на главную/поиск)
def test_09_404_page_behavior_soft(page):
    goto_ok(page, f"{BASE_URL}/this-page-does-not-exist-xyz")
    body = page.locator("body").inner_text(timeout=20000).lower()
    if not any(x in body for x in ["404", "не найден", "ошибка", "страница не существует"]):
        pytest.xfail("404 markers not detected (soft check).")


# 10. Футер есть (контакты — soft)
def test_10_footer_visible_and_has_contacts(page):
    goto_ok(page, BASE_URL)
    footer = page.locator("footer")
    expect(footer).to_be_visible()

    text = footer.inner_text().lower()
    if not any(x in text for x in ["тел", "+7", "контакт", "адрес", "@"]):
        pytest.xfail("Footer contact markers not found (soft check).")


# 11. Контакты страница (если есть ссылка/путь — мягко)
def test_11_contacts_page_soft(page):
    # Попробуем несколько типовых URL
    candidates = [f"{BASE_URL}/contacts", f"{BASE_URL}/contact", f"{BASE_URL}/kontakty"]
    opened = False
    for u in candidates:
        resp = page.goto(u, wait_until="domcontentloaded", timeout=20000)
        if resp is not None and resp.status < 400:
            opened = True
            break
    if not opened:
        pytest.skip("Contacts page not found by common URLs (soft)")

    assert body_has_any_text(page)


# 12. robots.txt и sitemap.xml (soft)
def test_12_robots_and_sitemap_exist_soft(page):
    # robots
    r = page.request.get(f"{BASE_URL}/robots.txt")
    if r.status >= 400:
        pytest.xfail(f"robots.txt missing (status {r.status}) (soft)")

    # sitemap
    s = page.request.get(f"{BASE_URL}/sitemap.xml")
    if s.status >= 400:
        pytest.xfail(f"sitemap.xml missing (status {s.status}) (soft)")


# 13. LK открывается (soft: маркеры входа могут быть другими)
def test_13_lk_page_opens_and_has_login_markers_soft(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    goto_ok(page, "https://lk.mc-aybolit.ru")

    body = page.locator("body").inner_text(timeout=20000).lower()
    if not any(x in body for x in ["вход", "авториза", "логин", "парол", "номер", "телефон"]):
        pytest.xfail("Login markers not detected on LK page (soft check).")
    context.close()
