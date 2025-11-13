import uuid

import pytest

from .constants import USER
from .pages.labels import LabelsPage
from .pages.login import LoginPage


@pytest.fixture()
def labels_page(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.login(USER["login"], USER["password"])
    page = LabelsPage(driver, base_url)
    assert page.delete_all_labels()
    assert page.create_label("Label_Name")
    return page


@pytest.fixture()
def seeded_label(labels_page):
    name = f"Label_{uuid.uuid4().hex[:5]}"
    assert labels_page.create_label(name)
    return labels_page, name


def test_create_label(labels_page):
    name = f"New_Label_{uuid.uuid4().hex[:5]}"
    assert labels_page.create_label(name)


def test_view_labels_list(labels_page):
    labels_page.open_page()
    labels_page.wait_for_text("Label_Name")
    assert labels_page.get_table() is not None


def test_edit_label(seeded_label):
    labels_page, name = seeded_label
    new_name = f"{name} Updated"
    assert labels_page.edit_label(name, new_name)


def test_delete_label(seeded_label):
    labels_page, name = seeded_label
    assert labels_page.delete_label(name)


def test_delete_all_labels(seeded_label):
    labels_page, name = seeded_label
    assert labels_page.delete_all_labels()

