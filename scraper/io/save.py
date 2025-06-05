
import logging
import pandas as pd

def save_job_data(jobs: list, unwanted_jobs: list, new_jobs_file: str, unwanted_jobs_file: str) -> None:
    new_jobs_df = pd.DataFrame(jobs).drop_duplicates(subset=["company", "title"])
    unwanted_jobs_df = pd.DataFrame(unwanted_jobs).drop_duplicates(subset=["company", "title"])

    new_jobs_df.to_csv(new_jobs_file, index=False)
    unwanted_jobs_df.to_csv(unwanted_jobs_file, index=False)

    logging.info(f"Saved {len(new_jobs_df)} new jobs to {new_jobs_file}")
    logging.info(f"Saved {len(unwanted_jobs_df)} unwanted jobs to {unwanted_jobs_file}")
