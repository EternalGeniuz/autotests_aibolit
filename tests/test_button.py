from playwright.sync_api import expect
import re


def test_online_appointment_link_opens_page(page, base_url):
    """
    Блок про онлайн-запись отображается на главной, а страница записи доступна.
    """
    page.goto(base_url, wait_until="domcontentloaded")

    online_text = page.get_by_text("Запись на прием", exact=False)
    expect(online_text.first).to_be_visible()

    page.goto(f"{base_url}/appointment/", wait_until="domcontentloaded")

    current_url = page.url
    assert (
        "/appointment" in current_url
        or re.search(r"lk\.mc-aybolit\.ru.*zapis", current_url)
    ), f"Неожиданный URL страницы записи: {current_url!r}"
