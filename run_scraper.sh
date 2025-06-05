#!/bin/bash

echo "Activating venv..."
source venvScraper/Scripts/activate

echo "starting the first run"

#make the script "be" in the correct place
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"


python "./scraper/call_scraper.py" --location "Israel" --pages 2  --jobsFile "./csv/new_jobs.csv" --unwantedJobsFile "./csv/unwanted_jobs.csv" --keywords '["Software Engineer", "Software Developer", "Backend Engineer", "Backend Developer" ]'
#
#echo "finished first runs, starting second"
#python "../python/call_scraper.py" --location "Israel" --pages 20  --jobsFile "../csv/new_jobs_2.csv" --unwantedJobsFile "../csv/unwanted_jobs_2.csv" --keywords '["Developer", "Programmer", "Full Stack Developer", "Junior Developer"]'
#
#echo "done"