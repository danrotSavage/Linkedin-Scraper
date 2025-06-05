# scraper/logic/scraper.py

import logging
import os
import time
import random
import traceback

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from scraper.logic.cookies import load_cookies
from scraper.logic.filters import (
    filter_by_company, filter_by_title, filter_by_location,
    filter_by_date, filter_by_description, clean_string, filter_viewed_jobs
)

company_skip = 0
title_skip = 0
location_skip = 0
date_skip = 0
reviewed = 0
total_viewed = 0


#todo log the skips and reviewed
def scrape_linkedin_jobs(job_title: str, location: str, pages: int = 1):
    global total_viewed, company_skip, title_skip, location_skip, date_skip
    logging.info(f"Starting LinkedIn job scrape for job_title={job_title} in location={location} with pages={pages}...")

    try:
        reviewed_jobs_df = pd.read_csv("./csv/reviewed_jobs.csv")
        logging.info(f"read {len(reviewed_jobs_df)} of reviewed jobs")

    except Exception:
        reviewed_jobs_df = pd.DataFrame(columns=["title", "company"])
        logging.error(f"from DataFrame read {len(reviewed_jobs_df)} of reviewed jobs")

    # Set up Chrome driver,  options to maximize the window
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    load_cookies(driver, "./resources/linkedin_cookies.json")

    jobs = []
    unwanted_jobs = []


    for page_num in range(pages):
        start = page_num * 25
        url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&start={start}&f_TPR=r604800"
        driver.get(url)
        time.sleep(2)

        scroll_down(driver)

        cards = driver.find_elements(By.CLASS_NAME, "job-card-container")

        #todo at least 2 function, also check if it even works now

        print("-------------printing cards-----------")
        for job in jobs:


            company = job.find_element(By.CLASS_NAME, "artdeco-entity-lockup__subtitle").text

            print(f"title={title}, company={company}")



        for card in cards:
            try:

                title, company, location = get_job_basic_info(card)

                if filter_viewed_jobs(company, title, reviewed_jobs_df):
                    continue
                #todo add a decorator here, that also does lower.
                if filter_by_company(company):
                    company_skip += 1
                    continue
                if filter_by_title(title):
                    title_skip += 1
                    continue
                if filter_by_location(location):
                    location_skip += 1
                    continue

                #todo from here is chatGPT guessing, find the location, date, description.

                date = get_job_date(card)
                if filter_by_date(date):
                    date_skip += 1
                    continue



                try:
                    description,job_link = get_job_description(driver, card)

                    if filter_by_description(description.lower()):
                        continue
                except Exception:
                    description = None
                    job_link = None

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": description,
                    "date": date,
                    "link": job_link,
                    "employees": -1,
                })
            except Exception as e:
                logging.error(f"Error while parsing card: {e}\n{traceback.format_exc()}")

        total_viewed += len(cards)

    driver.quit()
    return jobs, unwanted_jobs




###webpage functions
def scroll_down(driver):
    try:
        scrollable = driver.find_element(By.CSS_SELECTOR, "div.scaffold-layout__list > div")
        overflow_y = driver.execute_script("return window.getComputedStyle(arguments[0]).overflowY;", scrollable)
        if overflow_y not in ["auto", "scroll"]:
            logging.warning("Element is not scrollable")
    except Exception:
        logging.error("Failed to find scrollable container")
        scrollable = None

    if scrollable:
        last_height = 0
        for _ in range(50):
            driver.execute_script(f"arguments[0].scrollBy(0, {random.randint(200, 400)});", scrollable)
            time.sleep(random.choice([i * 0.1 for i in range(21)]) ) # 0 to 2.0 inclusive
            new_height = driver.execute_script("return arguments[0].scrollTop", scrollable)
            if new_height == last_height:
                break
            last_height = new_height











###get data functions
#get job title,company and location
def get_job_basic_info (card):
    title = card.find_element(By.CLASS_NAME, "job-card-list__title--link").text.split("\n")[0]
    company = card.find_element(By.CLASS_NAME, "artdeco-entity-lockup__subtitle").text
    location_el = card.find_element(By.CLASS_NAME, "job-search-card__location")
    location = location_el.text.strip() if location_el else ""

    return title.lower() ,company.lower() ,location.lower()

def get_job_date(card):
    job_date_el = card.find_elements(By.CLASS_NAME, "job-search-card__listdate") or \
                  card.find_elements(By.CLASS_NAME, "job-search-card__listdate--new")
    date = job_date_el[0].text.strip() if job_date_el else ""
    return date.lower()

def get_job_description(driver, card):
    job_link = card.find_element(By.CLASS_NAME, "base-card__full-link").get_attribute("href")
    driver.get(job_link)
    time.sleep(random.uniform(1, 2))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    desc_div = soup.find("div", class_="description__text description__text--rich")
    description = clean_string(desc_div.text.strip()) if desc_div else ""

    return description , job_link


def start_scrape(keywords, location: str, pages_to_review: int):
    all_jobs, all_unwanted = [], []
    for keyword in keywords:
        jobs, unwanted = scrape_linkedin_jobs(keyword, location, pages_to_review)
        all_jobs.extend(jobs)
        all_unwanted.extend(unwanted)

    #todo updated return code
    if not all_jobs and not all_unwanted:
        return None, None, 0
    if not all_jobs:
        return None, None , 1
    if not all_unwanted:
        return None, None , 2
    return all_jobs, all_unwanted, 3





























