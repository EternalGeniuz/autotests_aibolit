from playwright.sync_api import expect


def test_addresses_and_schedule_section_visible(page, base_url):
    """
    Блок «Адреса и режимы работы наших медицинских центров» доступен и не пустой.
    """
    page.goto(base_url, wait_until="domcontentloaded")

    addresses_block = page.get_by_text(
        "Адреса и режимы", exact=False
    ).locator("xpath=ancestor::*[1]")

    expect(addresses_block).to_be_visible()

    text = addresses_block.inner_text().strip()
    assert "работы наших медицинских центров" in text, (
        "В блоке адресов нет ожидаемого текста о режимах работы"
    )
