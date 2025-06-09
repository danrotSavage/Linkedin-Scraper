
import argparse
import ast
import time
import logging
import os
from datetime import datetime

from scraper.logic.scraper import start_scrape
from scraper.io.save import save_job_data
from scraper.io.combine import combine_jobs

REVIEWED_JOBS = "./csv/reviewed_jobs.csv"


def main():
    # Configure logging
    os.makedirs("./logs", exist_ok=True)
    log_filename = f"./logs/scraping_{datetime.now().strftime('%Y-%m-%d__%H-%M-%S')}.log"
    logging.basicConfig(filename=log_filename, level=logging.INFO)


    logger =  logging.getLogger(__name__)


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
    logger.info(
        f"location: {args.location}, pages: {args.pages}, jobsFile: {args.jobsFile}, unwantedJobsFile: {args.unwantedJobsFile}, keywords: {args.keywords}"
    )
    print(
        f"Scraping jobs for: {keywords_list} in {args.location} (pages={args.pages})...",
        flush=True,
    )


    start_time = time.time()

    jobs, unwanted_jobs, code = start_scrape(keywords_list, args.location, args.pages)

    #todo change other cases(did only 3)
    if code == 0:
        logger.info("No jobs or unwanted jobs found. Exiting.")
    elif code == 1:
        logger.info("Only unwanted jobs found. Saving them...")
        save_job_data([], unwanted_jobs, args.jobsFile, args.unwantedJobsFile)
        combine_jobs(REVIEWED_JOBS, "", args.unwantedJobsFile)
    elif code == 2:
        logger.info("Only jobs found. Saving them...")
        save_job_data(jobs, [], args.jobsFile, args.unwantedJobsFile)
        combine_jobs(REVIEWED_JOBS, args.jobsFile, "")
    elif code == 3:
        save_job_data(jobs, unwanted_jobs, args.jobsFile, args.unwantedJobsFile)
        combine_jobs(REVIEWED_JOBS, jobs, unwanted_jobs)


    print(f"The program took: {round(time.time() - start_time)} seconds to run")


if __name__ == "__main__":
    main()