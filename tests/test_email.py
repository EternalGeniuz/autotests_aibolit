import re

import pytest
from playwright.sync_api import expect

EMAIL_HREF_RE = re.compile(r"^mailto:[^@\s]+@[^@\s]+\.[^@\s]+$")


def _footer(page):
    return page.locator("footer.footer")


def test_g7_h8_04_footer_emails_format_and_clickable(page):
    """
    Email-ссылки в футере кликабельны и в корректном формате.

    Берём email-ссылки из футера: footer.footer a[href^="mailto:"]
    """
    footer = _footer(page)
    footer.wait_for(state="visible")

    email_links = footer.locator('a[href^="mailto:"]')

    assert email_links.count() > 0, "В футере не найдено email-ссылок mailto:"

    for i in range(min(email_links.count(), 10)):
        a = email_links.nth(i)

        href = (a.get_attribute("href") or "").strip()
        assert href and href != "#", f"Некорректный href email-ссылки: {href!r}"
        assert EMAIL_HREF_RE.match(href), f"href email не в формате mailto:user@example.com: {href}"

        text = (a.inner_text() or "").strip()
        assert text, f"У email-ссылки пустой текст: href={href!r}"
        assert "@" in text, f"Текст email-ссылки не похож на email: {text!r}"

