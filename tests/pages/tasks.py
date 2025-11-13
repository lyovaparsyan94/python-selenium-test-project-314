import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from ..utils.logging import LOGGER_NAME
from ..utils.text import build_xpath_by_text
from .base import BasePage

logger = logging.getLogger(f"{LOGGER_NAME}.tasks")


class TasksPage(BasePage):
    route = "tasks"

    def open_page(self) -> None:
        self.open(self.route)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Create"]')))

    def create_task(
        self,
        title: str,
        content: str,
        assignee_email: str,
        status_name: str,
    ) -> bool:
        logger.info("Creating task %s", title)
        self.open_page()
        self.click_icon("Create")
        self.select_from_dropdown('input[name="assignee_id"]', assignee_email)
        self.fill_input('input[name="title"]', title)
        if content:
            self.fill_input('textarea[name="content"]', content)
        self.select_from_dropdown('input[name="status_id"]', status_name)
        self.click_icon("Save")
        self.open_page()
        try:
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, build_xpath_by_text("*", title)))
            )
            logger.info("Created task %s", title)
            return True
        except TimeoutException:
            logger.warning("Task %s not found after creation", title)
            return False

    def task_exists(self, title: str) -> bool:
        self.open_page()
        try:
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, build_xpath_by_text("*", title)))
            )
        except TimeoutException:
            return False
        return True

    def _task_card_xpath(self, title: str) -> str:
        heading_xpath = build_xpath_by_text("*", title)
        return f"{heading_xpath}/ancestor::div[contains(@class,'MuiCard-root')]"

    def _open_edit(self, title: str) -> None:
        card_xpath = self._task_card_xpath(title)
        self.wait.until(EC.presence_of_element_located((By.XPATH, card_xpath)))
        edit_xpath = (
            f"{card_xpath}//button[@aria-label='Edit'] | {card_xpath}//a[@aria-label='Edit']"
        )
        edit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, edit_xpath)))
        edit_button.click()

    def edit_task(
        self,
        title: str,
        *,
        new_title: str | None = None,
        new_content: str | None = None,
        new_status: str | None = None,
    ) -> bool:
        logger.info("Editing task %s", title)
        self.open_page()
        self._open_edit(title)

        if new_title is not None:
            title_field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="title"]')))
            title_field.send_keys(Keys.CONTROL + "a")
            title_field.send_keys(Keys.DELETE)
            title_field.send_keys(new_title)
        if new_content is not None:
            content_field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'textarea[name="content"]')))
            content_field.send_keys(Keys.CONTROL + "a")
            content_field.send_keys(Keys.DELETE)
            content_field.send_keys(new_content)
        if new_status is not None:
            self.select_from_dropdown('input[name="status_id"]', new_status)

        self.click_icon("Save")
        updated_title = new_title or title
        self.wait.until(EC.url_contains("#/tasks"))
        self.open_page()
        try:
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, build_xpath_by_text("*", updated_title)))
            )
            logger.info("Finished editing task %s", updated_title)
            return True
        except TimeoutException:
            logger.warning("Task %s not found after edit", updated_title)
            return False

    def open_task_details(self, title: str) -> None:
        self.open_page()
        card_xpath = self._task_card_xpath(title)
        show_xpath = (
            f"{card_xpath}//button[@aria-label='Show'] | {card_xpath}//a[@aria-label='Show']"
        )
        show_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, show_xpath)))
        show_button.click()

    def is_task_in_status(self, title: str, status_name: str) -> bool:
        self.open_page()
        column_xpath = (
            f"//*[normalize-space()='{status_name}']/following::div[@data-rfd-droppable-id][1]"
        )
        try:
            column = self.wait.until(EC.presence_of_element_located((By.XPATH, column_xpath)))
            column.find_element(By.XPATH, f".//div[contains(@class,'MuiCard-root')]//*[normalize-space()='{title}']")
        except TimeoutException:
            return False
        except NoSuchElementException:
            return False
        return True
