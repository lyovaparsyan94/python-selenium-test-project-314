import uuid

import pytest

from .constants import USER
from .pages.login import LoginPage
from .pages.users import UsersPage


@pytest.fixture()
def users_page(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.login(USER["login"], USER["password"])
    page = UsersPage(driver, base_url)
    page.delete_all_users()
    return page


@pytest.fixture()
def seeded_users_page(users_page):
    email = f"user-{uuid.uuid4().hex[:6]}@example.com"
    assert users_page.create_user(email, "Name", "Surname")
    return users_page, email


def test_create_user(users_page):
    users_page.create_user("test@example.com", "John", "Doe")
    users_page.wait_for_text("test@example.com")


def test_view_user_list(seeded_users_page):
    users_page, email = seeded_users_page
    users_page.open_page()
    users_page.wait_for_text("Email")
    users_page.wait_for_text(email)


def test_edit_user(seeded_users_page):
    users_page, email = seeded_users_page
    updated_name = "Updated Name"
    assert users_page.edit_user(email, updated_name)


def test_delete_user(seeded_users_page):
    users_page, email = seeded_users_page
    assert users_page.delete_user(email)


def test_delete_all_users(seeded_users_page):
    users_page, email = seeded_users_page
    assert users_page.delete_all_users()

