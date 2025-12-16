import re
import pytest


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
