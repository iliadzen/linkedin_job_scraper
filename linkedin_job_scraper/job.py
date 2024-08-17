from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging


logger = logging.getLogger(__name__)

class Job:
    def __init__(self, driver: webdriver, url: str):
        self.driver = driver
        self.url = url

    def get_job_description(self) -> str:
        """
        Parses the job description from the given URL.
        """
        self.driver.get(self.url)
        try:
            wait = WebDriverWait(self.driver, 5)
            show_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.show-more-less-html__button.show-more-less-html__button--more')))
            show_more_button.click()
            job_description = self.driver.find_element(By.CSS_SELECTOR, '.show-more-less-html.show-more-less-html').text
            return job_description
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Error while parsing the job description on {self.url}: {str(e)}")
            return None