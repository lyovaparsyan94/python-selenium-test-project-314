from .constants import USER
from .pages.login import LoginPage


def test_sign_in(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.login(USER["login"], USER["password"])
    assert login_page.is_logged_in()


def test_logout(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.login(USER["login"], USER["password"])
    login_page.logout()
    assert login_page.is_logged_out()

