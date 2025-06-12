import logging

import pandas as pd
from pandas import DataFrame

logger = logging.getLogger(__name__)
# saves the new jobs found, both wanted and unwanted, into the reviewed jobs file.
# unique key is [title + company]


def combine_jobs(reviewed_jobs_file: str, new_jobs: list, unwanted_jobs: list) -> None:


    new_jobs_df  = pd.DataFrame(new_jobs)
    unwanted_jobs_df  = pd.DataFrame(unwanted_jobs)


    try:
        reviewed_jobs_df = pd.read_csv(reviewed_jobs_file)
        logger.info(f"managed to read reviewed")
    except Exception:
        reviewed_jobs_df = pd.DataFrame(columns=["title", "company"])
    logger.info(f"read {len(reviewed_jobs_df)} from reviewed")

    combined_df = pd.concat([reviewed_jobs_df, new_jobs_df, unwanted_jobs_df])
    combined_df.drop_duplicates(subset=["company", "title"], inplace=True)
    combined_df.to_csv(reviewed_jobs_file, index=False)

    added = len(new_jobs_df) + len(unwanted_jobs_df)
    print(f"Saved combined reviewed jobs to {reviewed_jobs_file} (added {added} entries)")
