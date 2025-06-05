#!/bin/bash

echo "Activating venv..."
source venvScraper/Scripts/activate

echo "starting the first run"

#make the script "be" in the correct place
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"


echo "Running scraper..."
python -m scraper.cli.call_scraper \
  --location "Israel" \
  --pages 20 \
  --jobsFile "./csv/new_jobs.csv" \
  --unwantedJobsFile "./csv/unwanted_jobs.csv" \
  --keywords '["Software Engineer", "Software Developer", "Backend Engineer", "Backend Developer"]'