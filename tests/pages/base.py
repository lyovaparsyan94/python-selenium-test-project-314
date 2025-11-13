from __future__ import annotations

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..constants import DEFAULT_TIMEOUT
from ..utils.text import build_xpath_by_text


class BasePage:
    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    def open(self, fragment: str = "") -> None:
        fragment = fragment.lstrip("/")
        if fragment and not fragment.startswith("#/"):
            fragment = f"#/{fragment}"

        url = f"{self.base_url}/{fragment}" if fragment else self.base_url
        self.driver.get(url)

    def wait_for_text(self, text: str, tag: str = "*"):
        locator = (By.XPATH, build_xpath_by_text(tag, text))
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click_by_text(self, text: str, tag: str = "*"):
        element = self.wait_for_text(text, tag)
        element.click()
        return element

    def click_icon(self, aria_label: str):
        locator = (By.CSS_SELECTOR, f'[aria-label="{aria_label}"]')
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        return element

    def fill_input(self, selector: str, value: str):
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        field.clear()
        field.send_keys(value)
        return field

    def select_from_dropdown(self, selector: str, item_text: str):
        element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

        trigger = element
        if element.tag_name.lower() == "input":
            try:
                trigger = element.find_element(
                    By.XPATH,
                    "./parent::*//*[@role='combobox']",
                )
            except NoSuchElementException:
                trigger = element

        self.wait.until(lambda driver: trigger.is_displayed() and trigger.is_enabled())
        try:
            trigger.click()
        except Exception:  # noqa: BLE001
            self.driver.execute_script("arguments[0].click();", trigger)

        option_locator = (By.XPATH, build_xpath_by_text("li", item_text))
        option = self.wait.until(EC.element_to_be_clickable(option_locator))
        option.click()
        return option

