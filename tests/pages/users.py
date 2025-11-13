import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from ..utils.logging import LOGGER_NAME
from ..utils.text import build_xpath_by_text
from .base import BasePage

logger = logging.getLogger(f"{LOGGER_NAME}.users")


class UsersPage(BasePage):
    route = "users"

    def open_page(self) -> None:
        self.open(self.route)

    def create_user(self, email: str, first_name: str, last_name: str) -> bool:
        logger.info("Creating user %s", email)
        self.open_page()
        self.click_icon("Create")
        self.fill_input('input[name="email"]', email)
        self.fill_input('input[name="firstName"]', first_name)
        self.fill_input('input[name="lastName"]', last_name)
        self.click_icon("Save")
        self.open_page()
        try:
            self.wait_for_text(email)
            logger.info("Created user %s", email)
            return True
        except TimeoutException:
            logger.warning("User %s not visible after creation", email)
            return False

    def edit_user(self, email: str, new_first_name: str) -> bool:
        logger.info("Editing user %s -> %s", email, new_first_name)
        self.open_page()
        self.click_by_text(email)
        field = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="firstName"]'))
        )
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.DELETE)
        field.send_keys(new_first_name)
        self.click_icon("Save")
        self.open_page()
        try:
            self.wait_for_text(new_first_name)
            logger.info("Finished editing user %s", email)
            return True
        except TimeoutException:
            logger.warning("Updated name %s not visible after edit", new_first_name)
            return False

    def delete_user(self, email: str) -> bool:
        logger.info("Deleting user %s", email)
        self.open_page()
        self.click_by_text(email)
        self.click_icon("Delete")
        self.open_page()
        try:
            self.wait.until_not(
                EC.presence_of_element_located((By.XPATH, build_xpath_by_text("*", email))),
            )
            logger.info("Deleted user %s", email)
            return True
        except TimeoutException:
            logger.warning("User %s still visible after delete", email)
            return False

    def delete_all_users(self) -> bool:
        logger.info("Deleting all users")
        self.open_page()
        rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        if not rows:
            logger.info("No users to delete")
            return True

        for row in rows:
            checkbox = row.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
            if not checkbox.is_selected():
                checkbox.click()

        self.click_icon("Delete")
        self.open_page()
        try:
            self.wait_for_text("Do you want to add one?")
            logger.info("All users removed")
            return True
        except TimeoutException:
            logger.warning("Empty state not visible after delete all")
            return False

    def get_table(self):
        self.open_page()
        return self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, "table")))

