import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from ..utils.logging import LOGGER_NAME
from ..utils.text import build_xpath_by_text
from .base import BasePage

logger = logging.getLogger(f"{LOGGER_NAME}.statuses")


class StatusesPage(BasePage):
    route = "task_statuses"

    def open_page(self) -> None:
        self.open(self.route)

    def create_status(self, name: str, slug: str) -> bool:
        logger.info("Creating status %s (%s)", name, slug)
        self.open_page()
        self.click_icon("Create")
        self.fill_input('input[name="name"]', name)
        self.fill_input('input[name="slug"]', slug)
        self.click_icon("Save")
        self.open_page()
        try:
            self.wait_for_text(name)
            logger.info("Created status %s", name)
            return True
        except TimeoutException:
            logger.warning("Status %s not visible after creation", name)
            return False

    def edit_status(self, current_name: str, new_name: str) -> bool:
        logger.info("Editing status %s -> %s", current_name, new_name)
        self.open_page()
        self.click_by_text(current_name)
        field = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="name"]'))
        )
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.DELETE)
        field.send_keys(new_name)
        self.click_icon("Save")
        self.open_page()
        try:
            self.wait_for_text(new_name)
            logger.info("Finished editing status %s -> %s", current_name, new_name)
            return True
        except TimeoutException:
            logger.warning("New status name %s not visible after edit", new_name)
            return False

    def delete_status(self, name: str) -> bool:
        logger.info("Deleting status %s", name)
        self.open_page()
        self.click_by_text(name)
        self.click_icon("Delete")
        self.open_page()
        try:
            self.wait.until_not(
                EC.presence_of_element_located((By.XPATH, build_xpath_by_text("*", name))),
            )
            logger.info("Deleted status %s", name)
            return True
        except TimeoutException:
            logger.warning("Status %s still visible after delete", name)
            return False

    def delete_all_statuses(self) -> bool:
        logger.info("Deleting all statuses")
        self.open_page()
        try:
            checkbox = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'table thead tr th input[type="checkbox"]'),
                ),
            )
        except TimeoutException:
            logger.info("No statuses to delete")
            return True

        checkbox.click()
        self.click_icon("Delete")
        self.open_page()
        try:
            self.wait_for_text("Do you want to add one?")
            logger.info("All statuses removed")
            return True
        except TimeoutException:
            logger.warning("Empty state not visible after delete all")
            return False

