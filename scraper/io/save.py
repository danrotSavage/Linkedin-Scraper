
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def save_job_data(jobs: list, unwanted_jobs: list, new_jobs_file: str, unwanted_jobs_file: str) -> None:
    #make the new_jobs file based on date. or at least change the last one to date before overwriting it.


    new_jobs_df = pd.DataFrame(jobs).drop_duplicates(subset=["company", "title"])
    unwanted_jobs_df = pd.DataFrame(unwanted_jobs).drop_duplicates(subset=["company", "title"])

    new_jobs_df.to_csv(new_jobs_file, index=False)
    unwanted_jobs_df.to_csv(unwanted_jobs_file, index=False)

    logger.info(f"Saved {len(new_jobs_df)} new jobs to {new_jobs_file}")
    logger.info(f"Saved {len(unwanted_jobs_df)} unwanted jobs to {unwanted_jobs_file}")
