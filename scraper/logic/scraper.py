# scraper/logic/scraper.py

import logging
import os
import time
import random
import traceback

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scraper.logic.cookies import load_cookies
from scraper.logic.filters import (
    filter_by_company, filter_by_title, filter_by_location,
    filter_by_date, filter_by_description, filter_viewed_jobs
)

logger = logging.getLogger(__name__)
company_skip = 0
title_skip = 0
location_skip = 0
description_skip =0
date_skip = 0
reviewed = 0
total_viewed = 0

def document(message : str):
    print(message)
    #logger.info(message)


#todo log all the paremeters skips and reviewed
def scrape_linkedin_jobs(job_title: str, location: str, pages: int = 1):
    global total_viewed, company_skip, title_skip, location_skip, date_skip
    logger.info(f"Starting LinkedIn job scrape for job_title={job_title} in location={location} with pages={pages}...")

    #load reviewed jobs
    try:
        reviewed_jobs_df = pd.read_csv("./csv/reviewed_jobs.csv")
        logger.info(f"read {len(reviewed_jobs_df)} of reviewed jobs")

    except Exception:
        reviewed_jobs_df = pd.DataFrame(columns=["title", "company"])
        logger.error(f"from DataFrame read {len(reviewed_jobs_df)} of reviewed jobs")

    # Set up Chrome driver,  options to maximize the window
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    load_cookies(driver, "./resources/linkedin_cookies.json")

    #get new jobs
    jobs, unwanted_jobs = get_all_jobs(driver,job_title,pages,location, reviewed_jobs_df)
    logger.info(
        f"skipping metrics - company_skip={company_skip}, title_skip={title_skip}, "
        f"location_skip={location_skip}, date_skip={date_skip}, "
        f"description_skip={description_skip}, reviewed={reviewed}, total_viewed={total_viewed}"
    )


    driver.quit()
    return jobs, unwanted_jobs



def get_all_jobs(driver,job_title,pages,location, reviewed_jobs_df):
    global total_viewed, description_skip, reviewed
    #todo nothing done with unwanted jobs
    jobs = []
    unwanted_jobs = []
    for page_num in range(pages):

        load_page(driver, job_title, location, page_num)
        time.sleep(2)

        scroll_down(driver)

        cards = driver.find_elements(By.CLASS_NAME, "job-card-container")

        document(f"-------------printing cards page={page_num}-----------")

        for card in cards:
            try:
                title, company, location = get_job_basic_info(card)
                date = get_job_date(card)

                document(f"title={title}, company={company}, location={location}, date={date}")


                if filter_viewed_jobs(company, title, reviewed_jobs_df):
                    reviewed+=1
                    document("filtered by viewed")
                    continue


                if filter_jobs(company, title, location, date):
                    add_job(unwanted_jobs, title, company, location, date)
                    continue


                #todo get date from here.
                description, link, date_optional =  get_job_description(driver, card)
                if date_optional:
                    date = date_optional
                    #todo filter by date

                document(f" date={date}, description={description}, link={link}")



                if description and (filter_by_description(description)):
                    description_skip +=1
                    add_job(unwanted_jobs, title, company, location, date, description, link)
                    continue



                add_job(jobs,title,company,location,date,description, link)

            except Exception as e:
                logger.error(f"##################Error while parsing card: {e}\n{traceback.format_exc()}")

        total_viewed += len(cards)

    document(f"total_viewed={total_viewed}")
    return jobs, unwanted_jobs



def add_job (df_jobs, title, company, location, date, description=None, link=None):
    df_jobs.append({
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "date": date,
        "link": link,
    })



# f_TPR=r604800 - past week, its seconds
def load_page(driver, job_title, location, page_num ):
    start = page_num * 25
    url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&start={start}&f_TPR=r604800"
    driver.get(url)

#find the job section an scroll down to load all jobs
def scroll_down(driver):
    try:
        scrollable = driver.find_element(By.CSS_SELECTOR, "div.scaffold-layout__list > div")
        overflow_y = driver.execute_script("return window.getComputedStyle(arguments[0]).overflowY;", scrollable)
        if overflow_y not in ["auto", "scroll"]:
            logger.warning("Element is not scrollable")
    except Exception:
        logger.error("Failed to find scrollable container")
        scrollable = None

    if scrollable:
        last_height = 0
        for _ in range(50):
            driver.execute_script(f"arguments[0].scrollBy(0, {random.randint(200, 400)});", scrollable)
            time.sleep(random.uniform(0,2) ) # 0 to 2.0 inclusive
            new_height = driver.execute_script("return arguments[0].scrollTop", scrollable)
            if new_height == last_height:
                break
            last_height = new_height







###get data functions
#get job title,company and location
def get_job_basic_info (card):
    try:
        title = card.find_element(By.CLASS_NAME, "job-card-list__title--link").text.split("\n")[0]
        company = card.find_element(By.CLASS_NAME, "artdeco-entity-lockup__subtitle").text
        location = card.find_element(By.CLASS_NAME, "artdeco-entity-lockup__caption").text
        return title.lower(), company.lower(), location.lower()
    except NoSuchElementException as e:
        logger.warning(f"Missing element in job card: {e}")
        return None, None, None
    except Exception as e:
        logger.error(f"Unexpected error while parsing job card: {e}")
        return None, None, None

def get_job_date(card):
    date_one = card.find_element(By.CLASS_NAME, "job-card-container__footer-item").text.split("\n")[0]

    return date_one.lower()

def get_job_description(driver, card):
    description = link = date =  None
    try:
        link_one = card.find_element(By.CLASS_NAME, "job-card-list__title--link")
        link = link_one.get_attribute("href")

        #go to job link in new tab and get description
        original_tab = driver.current_window_handle
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(link)
        time.sleep(random.uniform(1, 2))


        wait = WebDriverWait(driver, 3)
        see_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.jobs-description__footer-button')))
        see_more_button.click()



        #todo remove About the job
        time.sleep(random.uniform(1, 2))
        description_unfromatted = driver.find_element(By.ID, "job-details").text
        description = description_unfromatted.replace("\n", " ")

        container = driver.find_element(
            By.CSS_SELECTOR,
            "div.job-details-jobs-unified-top-card__tertiary-description-container"
        )
        spans = container.find_elements(By.CSS_SELECTOR, "span.tvm__text.tvm__text--low-emphasis")

        for span in spans:
            text = span.text.lower()
            if any(keyword in text for keyword in ["ago", "day", "month", "hour", "week"]):
                date = text
                break


        driver.close()
        driver.switch_to.window(original_tab)
    except Exception as e:
        logger.error(f"##################Error while parsing description: {e}\n{traceback.format_exc()}")

    return description, link , date



# Return codes:
# 0 - no jobs, no unwanted jobs
# 1 - no jobs, only unwanted jobs
# 2 - only jobs, no unwanted jobs
# 3 - both jobs and unwanted jobs found
def start_scrape(keywords, location: str, pages_to_review: int):
    all_jobs, all_unwanted = [], []
    for keyword in keywords:
        jobs, unwanted = scrape_linkedin_jobs(keyword, location, pages_to_review)
        all_jobs.extend(jobs)
        all_unwanted.extend(unwanted)

    if not all_jobs and not all_unwanted:
        return [], [], 0
    if not all_jobs:
        return [], all_unwanted, 1
    if not all_unwanted:
        return all_jobs, [], 2
    return all_jobs, all_unwanted, 3


def filter_jobs(job_company, job_title, job_location, job_date):
    global company_skip, title_skip, location_skip, date_skip

    if filter_by_company(job_company.lower()):
        logger.info(f"++++ skipping {job_title} from {job_company} because of Company")
        company_skip += 1
        return True

    if filter_by_title(job_title.lower()):
        logger.info(f"++++ skipping {job_title} from {job_company} because of Title")
        title_skip += 1
        return True

    elif filter_by_location(job_location.lower()):
        logger.info(
            f"++++ skipping {job_title} from {job_company} because of Location"
        )
        location_skip += 1
        return True

    elif filter_by_date(job_date.lower()):
        logger.info(f"++++ skipping {job_title} from {job_company} because of Date")
        date_skip += 1
        return True

    return False


























