from combine_jobs import combine_jobs
import scraper_logic as sl


import argparse
import ast
import time
import logging

REVIEWED_JOBS = "../csv/reviewed_jobs.csv"


# Configure logging settings
logging.basicConfig(filename="../logs/scraping.log", level=logging.INFO)

# Create the parser
parser = argparse.ArgumentParser(description="A simple argument parser")

# Add arguments
parser.add_argument(
    "--location", type=str, help="location of jobs, i.e. Israel", required=False
)
parser.add_argument(
    "--pages",
    type=int,
    help="amount of times to scroll down in a search",
    required=False,
)
parser.add_argument("--jobsFile", type=str, help="file for the new jobs")
parser.add_argument(
    "--unwantedJobsFile", type=str, help="file for the new unwanted jobs"
)
parser.add_argument("--keywords", type=str, help="List of job titles to search for")


# Parse the arguments
args = parser.parse_args()
keywords_list = ast.literal_eval(args.keywords)

logging.info(
    f"location: {args.location}, pages: {args.pages}, jobsFile: {args.jobsFile}, unwantedJobsFile: {args.unwantedJobsFile}, keywords: {args.keywords}"
)
print(
    f"location: {args.location}, pages: {args.pages}, jobsFile: {args.jobsFile}, unwantedJobsFile: {args.unwantedJobsFile}, keywords: {args.keywords}",
    flush=True,
)

start_time = time.time()


jobs, unwanted_jobs, code = sl.start_scrape(keywords_list, args.location, args.pages)

if code == 0:
    logging.info("nothing found... exiting")
    logging.info(
        f"skipping stats by filter - \n Total viewed: {sl.total_viewed}\n Company: {sl.company_skip}, Title: {sl.title_skip}, Location: {sl.location_skip}, Date: {sl.date_skip}, Viewed previously: {sl.reviewed}"
    )

else:
    sl.save_job_data(jobs, unwanted_jobs, args.jobsFile, args.unwantedJobsFile)

combine_jobs(REVIEWED_JOBS, args.jobsFile, args.unwantedJobsFile)

print(f"The program took: {round(time.time() - start_time)} seconds to run")
