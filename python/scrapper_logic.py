# Import necessary packages for web scraping and logging
import logging

from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

# Configure logging settings
logging.basicConfig(filename="../logs/scraping.log", level=logging.INFO)

company_skip = 0
title_skip = 0
location_skip = 0
date_skip = 0
reviewed = 0
total_viewed=0


def scrape_linkedin_jobs(job_title: str, location: str, pages: int = None) -> list:
    global total_viewed
    """
    Scrape job listings from LinkedIn based on job title and location.

    Parameters
    ----------
    job_title : str
        The job title to search for on LinkedIn.
    location : str
        The location to search for jobs in on LinkedIn.
    pages : int, optional
        The number of pages of job listings to scrape. If None, all available pages will be scraped.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary represents a job listing
        with the following keys: 'job_title', 'company_name', 'location', 'posted_date',
        and 'job_description'.
    """

    # Log a message indicating that we're starting a LinkedIn job search
    logging.info(f'*************************************')
    logging.info(f'Starting LinkedIn job scrape for "{job_title}" in "{location}"...')

    # Sets the pages to scrape if not provided
    pages = pages or 1

    #Create a dataframe from reviewed jobs, if new create an empty one
    try:
        reviewed_jobs_df = pd.read_csv("../csv/reviewed_jobs.csv")
        logging.info(f"read {len(reviewed_jobs_df)} of reviewed jobs")
    except Exception as e:
        columns = ['title', 'company']
        reviewed_jobs_df = pd.DataFrame(columns=columns)

    # Set up the Selenium web driver
    driver = webdriver.Chrome()

    # Set up Chrome options to maximize the window
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # Initialize the web driver with the Chrome options
    driver = webdriver.Chrome(options=options)

    # Navigate to the LinkedIn job search page with the given job title and location
    #f_TPR=r604800 - past week, its seconds
    driver.get(
        f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&f_TPR=r604800"
    )

    # Scroll through the first 50 pages of search results on LinkedIn
    for i in range(pages):

        # Log the current page number
        logging.info(f"Scrolling to bottom of page {i + 1}...")

        # Scroll to the bottom of the page using JavaScript
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            # Wait for the "Show more" button to be present on the page
            element = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div/main/section[2]/button")
                )
            )
            # Click on the "Show more" button
            element.click()

        # Handle any exception that may occur when locating or clicking on the button
        except Exception:
            # Log a message indicating that the button was not found and we're retrying
            logging.info("Show more button not found, retrying...")

        # Wait for a random amount of time before scrolling to the next page
        time.sleep(random.randint(2,5))

    # Scrape the job postings
    jobs = []
    unwanted_jobs = []
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_listings = soup.find_all(
        "div",
        class_="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card",
    )
    total_viewed += len(job_listings)

    try:
        for job in job_listings:
            try:
                # Extract job details

                # job title
                job_title = job.find("h3", class_="base-search-card__title").text.strip()
                # job company
                job_company = job.find(
                    "h4", class_="base-search-card__subtitle"
                ).text.strip()

                #skipped viewed jobs, only need new ones
                if (filter_viewed_jobs(job_company, job_title, reviewed_jobs_df)):
                    continue

                # job location
                job_location = job.find(
                    "span", class_="job-search-card__location"
                ).text.strip()
                # job link
                apply_link = job.find("a", class_="base-card__full-link")["href"]
                #job posting date
                job_date = job.find(
                    "time", class_="job-search-card__listdate"
                )
                #sometimes date has the --new postfix
                job_date = job_date.text.strip() if (job_date is not None) else (
                    job.find("time", class_="job-search-card__listdate--new").text.strip())

                #apply filters
                if (filter_jobs(job_company, job_title, job_location, job_date)):
                    unwanted_jobs.append(
                        {
                            "title": job_title,
                            "company": job_company,
                            "location": job_location,
                            "description": "",
                            "date": job_date,
                            "link": apply_link,
                            "employees": -1,
                        }
                    )
                    continue

                #sleep to not pass request limit
                time.sleep(random.randrange(1,4))

                # Navigate to the job posting page and scrape the description
                driver.get(apply_link)

                # Use try-except block to handle exceptions when retrieving job description
                try:
                    # Create a BeautifulSoup object from the webpage source
                    description_soup = BeautifulSoup(driver.page_source, "html.parser")

                    # Find the job description element and extract its text
                    job_description = description_soup.find(
                        "div", class_="description__text description__text--rich"
                    ).text.strip()

                    #clean job description
                    job_description = clean_string(job_description)
                    if (filter_by_description(job_description.lower())):
                        continue

                # Handle the AttributeError exception that may occur if the element is not found
                except AttributeError:
                    # Assign None to the job_description variable to indicate that no description was found
                    job_description = None

                    # Write a warning message to the log file
                    logging.warning(
                        "AttributeError occurred while retrieving job description."
                    )

                #job filter here

                # Add job details to the jobs list
                jobs.append(
                    {
                        "title": job_title,
                        "company": job_company,
                        "location": job_location,
                        "description": job_description,
                        "date": job_date,
                        "link": apply_link,
                        "employees": -1,
                    }
                )
                # Logging scrapped job with company and location information
                logging.info(f'Found "{job_title}" at {job_company} in {job_location} from  {job_date}...')
            #if a single job fails not all should fail.
            except Exception as e:
                logging.error(f"An error occurred while scraping jobs: {str(e)}")


    # Catching any exception that occurs in the scrapping process
    except Exception as e:
        # Log an error message with the exception details
        logging.error(f"An error occurred while scraping jobs: {str(e)}")

        # Return the jobs list that has been collected so far
        # This ensures that even if the scraping process is interrupted due to an error, we still have some data
        return jobs

    # Close the Selenium web driver
    driver.quit()

    # Return the jobs list
    return jobs, unwanted_jobs


def save_job_data(jobs: dict, unwanted_jobs, new_jobs_file, unwanted_jobs_file) -> None:
    global company_skip, title_skip, location_skip, date_skip, reviewed , total_viewed
    """
    Save job data to a CSV file.

    Args:
        data: A dictionary containing job data.

    Returns:
        None
    """

    # Create a pandas DataFrame from the job data dictionary
    new_jobs_df = pd.DataFrame(jobs)
    new_jobs_df = new_jobs_df.drop_duplicates(subset=['company', 'title'])

    unwanted_jobs_df = pd.DataFrame(unwanted_jobs)
    unwanted_jobs_df = unwanted_jobs_df.drop_duplicates(subset=['company', 'title'])

    # Save the DataFrame to a CSV file without including the index column
    new_jobs_df.to_csv(new_jobs_file, index=False)
    unwanted_jobs_df.to_csv(unwanted_jobs_file, index=False)


    logging.info (f"skipping stats by filter - \n Total viewed: {total_viewed}\n Company: {company_skip}, Title: {title_skip}, Location: {location_skip}, Date: {date_skip}, Viewed previously: {reviewed}")

    # Log a message indicating how many jobs were successfully scraped and saved to the CSV file
    logging.info(f"Successfully scraped {len(new_jobs_df)} jobs and saved to {new_jobs_file}")
    logging.info(f"Successfully saved {len(unwanted_jobs_df)} unwanted jobs and saved to {unwanted_jobs_file}")


def filter_jobs(job_company, job_title, job_location, job_date):
    global company_skip, title_skip, location_skip, date_skip

    if filter_by_company(job_company.lower()):
        logging.info(f"++++ skipping {job_title} from {job_company} because of Company")
        company_skip += 1
        return True

    if filter_by_title(job_title.lower()):
        logging.info(f"++++ skipping {job_title} from {job_company} because of Title")
        title_skip += 1
        return True


    elif filter_by_location(job_location.lower()):
        logging.info(f"++++ skipping {job_title} from {job_company} because of Location")
        location_skip += 1
        return True

    elif filter_by_date(job_date.lower()):
        logging.info(f"++++ skipping {job_title} from {job_company} because of Date")
        date_skip += 1
        return True

    return False


#filter by company name, later on employee count
def get_employee_count(company_name: str) -> int:
    a = 8


def filter_by_company(company_name: str) -> bool:
    bad_companies = ["sqlink", "check point" , "elbit" , "rafael", "microsoft" , "wix"]
    for company in bad_companies:
        if company in company_name:
            return True
    return False


#filter by description
def filter_by_description(desc: str) -> bool:
    bad_substring = ["4+", "4 +", "5+", "5 +", "PHP" , "5 years" , "six years","8+"]
    for bad_string in bad_substring:
        if bad_string in desc:
            return True
    return False


#filter by title
def filter_by_title(title: str) -> bool:
    bad_substring = ["senior", "solutions", "data", "frontend", "remote", "react", "experienced" , "embedded", "qa" , "devops" , "android", "architect", "principal"
                     ,"automation" , "lead" ,"leader",  "product", "business intelligence" "c++", "angular" , "manager" , "sr." , "support" , "sre" , "system"
                     ,"sql" " ai ", "solution" , "firmware" , "ios " , "machine learning" , "decsecops" , "hardware", " it " , " go ","artificial intelligence" , "javascript"
                     ,"++" , "algorithm" , "unity" , "mobile" , "sap" , "idm" , "account executive" , " staff ", "infrastructure","cobol"]

    for bad_string in bad_substring:
        if bad_string in title:
            return True
    return False


# max 1 week ago
def filter_by_date(date_posted: str) -> bool:
    if ("month" in date_posted):
        return True
    if ("week" in date_posted and "1" not in date_posted):
        return True
    return False


# going for exclusion instead of inclusion to not miss out on opportunities because of misspelling.
def filter_by_location(location: str) -> bool:
    bad_locations = ["netanya", "modiin", "haifa", "remote", "hod hasharon" , "petah tikva", "raanana" ,"yokneam", "yoqneam" , "jerusalem",
                     "rosh haayin" , "rehovot" , "ramat hasharon", "karmiel" , "ahihud" , "be'er sheva", "veer yaakov", "kfar saba" , "omer", "south district",
                     "afikim","yakum", "migdal haemek" , "north district"]

    for bad_loc in bad_locations:
        if bad_loc in location:
            return True
    return False


def filter_viewed_jobs(company: str, job_title: str, reviewed_jobs_df: DataFrame) -> bool:
    global reviewed
    #if empty do not skip
    empty_df = not reviewed_jobs_df.query('company == @company and title == @job_title').empty
    if empty_df:
        logging.info(f"---- skipping {job_title} from {company}")
        reviewed+=1
    return empty_df


def clean_string(input_string: str) -> str:
    # Remove new lines
    cleaned_string = input_string.replace("\n", " ")
    # Remove "Show more"
    cleaned_string = cleaned_string.replace("Show more", "")
    return cleaned_string.strip()







def start_scrape(keywords, location :str  , pages_to_review : int):
    first_jobs = True
    first_unwanted = True

    jobs_df = None
    unwanted_jobs_df = None

    for key in keywords:
        jobs, unwanted_jobs = scrape_linkedin_jobs(key, location, pages_to_review)
        #if found something
        if len(jobs) != 0:
            if first_jobs:
                jobs_df=jobs
                first_jobs = False
            else:
                jobs_df.extend(jobs)

        if len(unwanted_jobs) != 0:
            if first_unwanted:
                unwanted_jobs_df=unwanted_jobs
                first_unwanted = False
            else:
                unwanted_jobs_df.extend(unwanted_jobs)





    #if found nothing
    if first_jobs and first_unwanted:
        return None ,None, 0
    else:
        return jobs_df, unwanted_jobs_df , 1


#
# data = scrape_linkedin_jobs("software engineer", "israel", PAGES_TO_REVIEW)
# data2 = scrape_linkedin_jobs("software developer", "israel", PAGES_TO_REVIEW)
# data3 = scrape_linkedin_jobs("backend", "israel", PAGES_TO_REVIEW)
# data4 = scrape_linkedin_jobs("developer", "israel", PAGES_TO_REVIEW)
#
# data_frames = [data, data2, data3, data4]
#
# non_empty_data_frames = [df for df in data_frames if not len(df) == 0]
#
# if(len (non_empty_data_frames))
# total_df  =  non_empty_data_frames if len pd.concat(non_empty_data_frames, ignore_index=True)
#
# # data_combined2= data.append(data2)

# data2 = scrape_linkedin_jobs("software developer", "israel", 30).append(data1)
# data3 = scrape_linkedin_jobs("backend", "israel", 30).append(data2)
# data4 = scrape_linkedin_jobs("developer", "israel", 30).append(data3)

# PAGES_TO_REVIEW = 20
# keywords1 = ["Software Engineer", "Software Developer", "Backend Engineer", "Backend Developer" ]
# keywords2 = ["Developer", "Programmer", "Full Stack Developer", "Junior Developer"]
#
#
#
#
#
# #jobs, unwanted_jobs,code = start_scrape(keywords1, "israel", PAGES_TO_REVIEW)
# jobs, unwanted_jobs,code = start_scrape(keywords2, "israel", PAGES_TO_REVIEW)







