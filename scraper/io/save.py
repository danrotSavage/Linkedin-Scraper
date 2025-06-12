
import logging
import os
from datetime import datetime

import pandas as pd
from pandas import DataFrame

logger = logging.getLogger(__name__)



output_dir = './csv'


def save_job_data(jobs: DataFrame, unwanted_jobs: DataFrame) -> None:
    #make the new_jobs file based on date. or at least change the last one to date before overwriting it.
    os.makedirs(output_dir, exist_ok=True)

    new_jobs_df = pd.DataFrame(jobs).drop_duplicates(subset=["company", "title"])
    unwanted_jobs_df = pd.DataFrame(unwanted_jobs).drop_duplicates(subset=["company", "title"])

    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    new_jobs_path = os.path.join(output_dir, f"new_jobs-{date_str}.csv")
    unwanted_jobs_path = os.path.join(output_dir, f"unwanted-jobs-{date_str}.csv")

    new_jobs_df.to_csv(new_jobs_path, index=False)
    unwanted_jobs_df.to_csv(unwanted_jobs_path, index=False)

    logger.info(f"Saved {len(new_jobs_df)} new jobs to {new_jobs_path}")
    logger.info(f"Saved {len(unwanted_jobs_df)} unwanted jobs to {unwanted_jobs_path}")
