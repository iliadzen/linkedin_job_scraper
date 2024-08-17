import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from .scraping_utils import create_query_string
import logging


logger = logging.getLogger(__name__)

BASE_SEARCH_URL = 'https://www.linkedin.com/jobs/search'
SCROLL_PAUSE_TIME = 5
MAX_SEARCH_EXPANDINGS = 10
SEARCH_LOADING_TIMEOUT = 60

class JobSearch:
    """
    A class to scrape a job search page in LinkedIn.
    """
    def __init__(
            self, 
            driver: webdriver,
            keywords: str,
            location: str,
            distance: int = 25, # in miles
            work_modes: list = None,
            industries: list = None,
            company_codes: list = None,
            experience_levels: list = None,
            easy_apply: bool = None,
            posted_ago_max: int = 86400 # in seconds
        ):
        """
        Inits JobSearch with search parameters.

        Args:
            keywords (str): keywords to search for.
            location (str): location to search in.
            distance (int, optional): distance in miles to search for.
            work_modes (list, optional): work modes codes to filter by: 1-On-site, 2-Remote, 3-Hybrid, None-all.
            company_codes (list, optional): companies codes to filter by.
            industries (list, optional): industries codes to filter by.
            experience_levels (list, optional): experience levels to filter by: 1-Internship, 2-Entry level, 3-Associate, 4-Mid-Senior level, 5-Director, 6-Executive.
            easy_apply (bool, optional): filter only Easy Apply jobs.
            posted_ago_max (int, optional): max number of second a job was posted ago, default 1 day.
        """
        self.driver = driver
        self.keywords = keywords
        self.location = location
        self.distance = distance
        self.work_modes = work_modes
        self.industries = industries
        self.company_codes = company_codes
        self.experience_levels = experience_levels
        self.easy_apply = easy_apply
        self.posted_ago_max = posted_ago_max

    def get_search_url(self) -> str:
        """
        Generates a search URL based on the given parameters.
        """
        params = {
            'currentJobId': '',
            'keywords': self.keywords,
            'location': self.location,
            'distance': self.distance,
            'f_C': self.company_codes,
            'f_WT': self.work_modes,
            'f_I': self.industries,
            'f_E': self.experience_levels,
            'f_TPR': f'r{self.posted_ago_max}',
            'f_AL': 'true' if self.easy_apply else None
        }
        params = {p: v for p, v in params.items() if v is not None} # remove empty parameters
        url = BASE_SEARCH_URL + '/?' + create_query_string(params)
        return url

    def _check_if_search_page_fully_loaded(self) -> bool:
        """
        Scrolls through the job search page to ensure all jobs are loaded.
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        s = 0
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            logger.info(f'Scrolled down {s + 1} times')
            s += 1

        logger.info('Scrolling finished')

        try:
            self.driver.find_element(By.XPATH, "//*[contains(text(), \"You've viewed all jobs for this search\")]")
            logger.info("All the jobs for this search have been viewed")
            return True
        except NoSuchElementException:
            pass

        try:
            show_more_button = self.driver.find_element(By.CSS_SELECTOR, '.infinite-scroller__show-more-button.infinite-scroller__show-more-button--visible')
            show_more_button.click()
            logger.info('Clicked "See more jobs"')
            return False
        except NoSuchElementException:
            logger.info("No more 'See more jobs' button found")
            return True

    def _parse_jobs_search_page(self, url: str) -> list:
        """
        Parses the job search and returns a list of job cards.
        """
        self.driver.get(url)
        wait = WebDriverWait(self.driver, SEARCH_LOADING_TIMEOUT)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class^="base-card"]')))
        except Exception as e:
            logger.error(f"Error waiting for job cards: {e}")
            return

        n = 0
        end = False
        while not end and n < MAX_SEARCH_EXPANDINGS:
            end = self._check_if_search_page_fully_loaded()
            n += 1

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        pattern = re.compile(r'base-card.*')
        return soup.find_all(attrs={"class": pattern})

    def _parse_job_search_card(self, card: BeautifulSoup) -> dict:
        """
        Parses a job card and returns a dictionary of card information.
        """
        job_title = card.find('h3', class_='base-search-card__title')
        if job_title is None:
            return
        job_title = job_title.get_text(strip=True)
        company_name = card.find('h4', class_='base-search-card__subtitle').get_text(strip=True)
        job_link = card.find('a', class_='base-card__full-link')
        if job_link is None:
            return
        job_link = job_link['href']
        posted = card.find('time', class_='job-search-card__listdate--new')
        if posted is None:
            posted = card.find('time', class_='job-search-card__listdate')
        posted = re.sub(r'\n+', '\n', posted.text).strip()
        location = card.find('span', class_='job-search-card__location').get_text(strip=True)
        return {
            "job_title": job_title,
            "company_name": company_name,
            "posted": posted,
            "job_link": job_link,
            "location": location
        }
        
    
    def get_jobs(self) -> list:
        """
        Finds and parses jobs from a search page by defined parameters.
        """
        url = self.get_search_url()
        found_job_cards = self._parse_jobs_search_page(url)
        if found_job_cards is None:
            logger.error(f'No jobs found for {url}')
            return

        logger.info(f'Found {len(found_job_cards)} jobs for {url}')
        jobs = []
        for job_elem in found_job_cards:
            job = self._parse_job_search_card(job_elem)
            if job:
                jobs.append(job)
        return jobs
