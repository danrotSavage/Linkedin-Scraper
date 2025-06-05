
import argparse
import ast
import time
import logging
import os

from scraper.logic.scraper import start_scrape
from scraper.io.save import save_job_data
from scraper.io.combine import combine_jobs

REVIEWED_JOBS = "./csv/reviewed_jobs.csv"


def main():
    # Configure logging
    os.makedirs("./logs", exist_ok=True)
    logging.basicConfig(filename="./logs/scraping.log", level=logging.INFO)


    # Argument parsing
    parser = argparse.ArgumentParser(description="LinkedIn Job Scraper CLI")
    parser.add_argument("--location", type=str, required=False, help="Job location")
    parser.add_argument("--pages", type=int, required=False, help="Number of scroll pages")
    parser.add_argument("--jobsFile", type=str, required=True, help="Output file for wanted jobs")
    parser.add_argument("--unwantedJobsFile", type=str, required=True, help="Output file for unwanted jobs")
    parser.add_argument("--keywords", type=str, required=True, help="List of job titles (as Python list string)")


    args = parser.parse_args()
    keywords_list = ast.literal_eval(args.keywords)

    # Log params
    logging.info(
        f"location: {args.location}, pages: {args.pages}, jobsFile: {args.jobsFile}, unwantedJobsFile: {args.unwantedJobsFile}, keywords: {args.keywords}"
    )
    print(
        f"Scraping jobs for: {keywords_list} in {args.location} (pages={args.pages})...",
        flush=True,
    )


    start_time = time.time()

    jobs, unwanted_jobs, code = start_scrape(keywords_list, args.location, args.pages)

    #todo add cases of 1,2,3 code
    if code == 0:
        logging.info("nothing found... exiting")
        logging.info(
            f"skipping stats by filter - \n Total viewed: {sl.total_viewed}\n Company: {sl.company_skip}, Title: {sl.title_skip}, Location: {sl.location_skip}, Date: {sl.date_skip}, Viewed previously: {sl.reviewed}"
        )

    else:
        save_job_data(jobs, unwanted_jobs, args.jobsFile, args.unwantedJobsFile)

    #todo add another code for didn't find jobs but have unwanted.
    #if no new jobs found still could find jobs that are not useful
    combine_jobs(REVIEWED_JOBS, args.jobsFile, args.unwantedJobsFile)

    print(f"The program took: {round(time.time() - start_time)} seconds to run")


if __name__ == "__main__":
    main()