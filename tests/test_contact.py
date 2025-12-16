import re
import pytest
from playwright.sync_api import expect


PHONE_HREF_RE = re.compile(r"^tel:\+?7\d{10}$")


def _footer(page):
    return page.locator("footer.footer")


def test_g7_h8_01_phones_format_and_clickable(page):
    """
    H8-01: Телефоны кликабельны и в корректном формате.
    Берём телефоны из футера: .footer__phones a.footer__phone_number
    """
    footer = _footer(page)
    footer.wait_for(state="visible")

    tel_links = footer.locator('.footer__phones a.footer__phone_number[href^="tel:"]')
    assert tel_links.count() > 0, "В футере не найдено ссылок tel: в .footer__phones"

    for i in range(min(tel_links.count(), 10)):
        a = tel_links.nth(i)
        href = (a.get_attribute("href") or "").strip()
        assert href and href != "#", f"Некорректный href телефона: {href!r}"
        assert PHONE_HREF_RE.match(href), f"href телефона не в формате tel:+7XXXXXXXXXX: {href}"

        text = (a.inner_text() or "").strip()
        assert text.startswith("+7"), f"Текст телефона не начинается с +7: {text!r}"


def test_g7_h8_03_social_links_are_external_and_not_empty(page):
    """
    H8-03: Соцсети в футере присутствуют и ведут наружу.
    Берём ссылки из .footer__social .social__links a.social_links_item
    """
    footer = _footer(page)
    footer.wait_for(state="visible")

    social = footer.locator(".footer__social .social__links a.social_links_item")
    assert social.count() > 0, "В футере не найден блок соцсетей (.footer__social .social__links)"

    for i in range(min(social.count(), 10)):
        a = social.nth(i)
        href = (a.get_attribute("href") or "").strip()

        assert href and href != "#", f"Пустой/плохой href у соцссылки: {href!r}"
        assert href.startswith("https://") or href.startswith("http://"), f"Соцссылка не внешняя: {href}"


def test_g7_h8_03_footer_social_links_exact(page, base_url):
    """
    H8-03: В футере отображаются соцсети и ссылки соответствуют ожидаемым (строго по HTML).
    """
    page.goto(base_url, wait_until="domcontentloaded")

    footer = page.locator("footer.footer")
    expect(footer).to_be_visible()

    social_links = footer.locator(".footer__social .social__links a.social_links_item")
    expect(social_links).to_have_count(4)

    expected = {
        "https://vk.com/mc_aybolit",
        "https://wa.me/78432554141",
        "https://t.me/mcaybolit",
        "https://www.instagram.com/aybolit_kazan/",
    }

    actual = set()
    for i in range(social_links.count()):
        href = (social_links.nth(i).get_attribute("href") or "").strip()
        actual.add(href)

    assert actual == expected, f"Ссылки соцсетей не совпали.\nExpected: {expected}\nActual:   {actual}"
