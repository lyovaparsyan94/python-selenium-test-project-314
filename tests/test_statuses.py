import uuid

import pytest

from .constants import USER
from .pages.login import LoginPage
from .pages.statuses import StatusesPage


@pytest.fixture()
def statuses_page(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.login(USER["login"], USER["password"])
    page = StatusesPage(driver, base_url)
    page.delete_all_statuses()
    return page


@pytest.fixture()
def seeded_status(statuses_page):
    name = f"Status {uuid.uuid4().hex[:5]}"
    slug = f"slug-{uuid.uuid4().hex[:5]}"
    assert statuses_page.create_status(name, slug)
    return statuses_page, name, slug


def test_create_status(statuses_page):
    name = f"Backlog {uuid.uuid4().hex[:5]}"
    slug = f"backlog-{uuid.uuid4().hex[:5]}"
    assert statuses_page.create_status(name, slug)


def test_view_statuses_list(statuses_page):
    statuses_page.open_page()
    statuses_page.wait_for_text("Name")
    statuses_page.wait_for_text("Slug")


def test_edit_status(seeded_status):
    statuses_page, name, slug = seeded_status
    new_name = f"{name} Updated"
    assert statuses_page.edit_status(name, new_name)


def test_delete_status(seeded_status):
    statuses_page, name, _ = seeded_status
    assert statuses_page.delete_status(name)


def test_delete_all_statuses(seeded_status):
    statuses_page, name, _ = seeded_status
    assert statuses_page.delete_all_statuses()

