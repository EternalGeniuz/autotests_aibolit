import os
import pytest
from playwright.sync_api import sync_playwright
from datetime import datetime

BASE_URL = os.getenv("BASE_URL", "https://mc-aybolit.ru").rstrip("/")

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance):
    headless = os.getenv("HEADLESS", "1") != "0"
    browser = playwright_instance.chromium.launch(headless=headless)
    yield browser
    browser.close()

@pytest.fixture
def context(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    yield ctx
    ctx.close()

@pytest.fixture
def page(context):
    page = context.new_page()
    page.goto(BASE_URL, timeout=30000, wait_until="domcontentloaded")
    yield page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            os.makedirs("artifacts", exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=f"artifacts/{item.name}_{ts}.png")