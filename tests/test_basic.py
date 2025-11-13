from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .constants import DEFAULT_TIMEOUT


def test_application_renders(driver, base_url):
    driver.get(base_url)
    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
    element = wait.until(EC.visibility_of_element_located((By.XPATH, '//button[.="Sign in"]')))
    assert element is not None

