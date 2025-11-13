import logging
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from ..constants import DEFAULT_TIMEOUT
from ..utils.logging import LOGGER_NAME
from ..utils.text import build_xpath_by_text
from .base import BasePage

logger = logging.getLogger(f"{LOGGER_NAME}.labels")


class LabelsPage(BasePage):
    route = "labels"

    def _label_locator(self, name: str):
        return By.XPATH, build_xpath_by_text("*", name)

    def wait_until_label_present(self, name: str, timeout: int = DEFAULT_TIMEOUT):
        locator = self._label_locator(name)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.driver.find_elements(*locator):
                return
            time.sleep(0.5)
        raise TimeoutException(f"Label '{name}' not found")

    def wait_until_label_absent(self, name: str, timeout: int = DEFAULT_TIMEOUT):
        locator = self._label_locator(name)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not self.driver.find_elements(*locator):
                return
            time.sleep(0.5)
        raise TimeoutException(f"Label '{name}' still present")

    def wait_for_notification(self, text: str, timeout: int = DEFAULT_TIMEOUT):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if text in self.driver.page_source:
                return
            time.sleep(0.2)
        raise TimeoutException(f"Notification '{text}' not shown")

    def open_page(self) -> None:
        self.open(self.route)

    def create_label(self, name: str) -> bool:
        logger.info("Creating label %s", name)
        self.open_page()
        time.sleep(0.2)
        self.click_icon("Create")
        time.sleep(0.2)
        self.fill_input('input[name="name"]', name)
        time.sleep(0.2)
        self.click_icon("Save")
        time.sleep(0.2)

        self.wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, '[role="dialog"]')),
        )
        self.wait_for_notification("Element created")
        time.sleep(1)
        self.open_page()
        success = True
        try:
            self.wait_until_label_present(name, timeout=DEFAULT_TIMEOUT * 3)
        except TimeoutException:
            logger.warning("Label %s not visible after creation", name)
            success = False
        logger.info("Created label %s -> %s", name, success)
        return success

    def edit_label(self, current_name: str, new_name: str) -> bool:
        logger.info("Editing label %s -> %s", current_name, new_name)
        self.open_page()
        self.click_by_text(current_name)
        field = self.fill_input('input[name="name"]', "")
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.DELETE)
        field.send_keys(new_name)
        logger.debug("Input value after edit: %s", field.get_attribute("value"))
        self.click_icon("Save")
        self.wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, '[role="dialog"]')),
        )
        self.wait_for_notification("Element updated")
        time.sleep(1)
        success = True
        try:
            self.wait_until_label_absent(current_name)
        except TimeoutException:
            logger.warning("Old label %s still visible after edit", current_name)
            success = False
        self.open_page()
        try:
            self.wait_until_label_present(new_name, timeout=DEFAULT_TIMEOUT * 3)
        except TimeoutException:
            logger.warning("New label %s not visible after edit", new_name)
            success = False
        logger.info(
            "Finished editing label %s -> %s (success=%s)",
            current_name,
            new_name,
            success,
        )
        return success

    def delete_label(self, name: str) -> bool:
        logger.info("Deleting label %s", name)
        self.open_page()
        self.click_by_text(name)
        self.click_icon("Delete")
        self.open_page()
        try:
            self.wait_until_label_absent(name)
            logger.info("Deleted label %s", name)
            return True
        except TimeoutException:
            logger.warning("Label %s still visible after delete", name)
            return False

    def delete_all_labels(self) -> bool:
        logger.info("Deleting all labels")
        self.open_page()
        try:
            checkbox = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'table thead tr th input[type="checkbox"]'),
                ),
            )
        except TimeoutException:
            logger.info("No labels to delete")
            return True

        checkbox.click()
        self.click_icon("Delete")
        self.open_page()
        try:
            self.wait_for_text("Do you want to add one?")
            logger.info("All labels removed")
            return True
        except TimeoutException:
            logger.warning("Empty state not visible after delete all")
            return False

    def get_table(self):
        self.open_page()
        return self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, "table")))

