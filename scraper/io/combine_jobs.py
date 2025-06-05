import pandas as pd

# saves the new jobs found, both wanted and unwanted, into the reviewed jobs file.
# unique key is [title + company]


def combine_jobs(reviewed_jobs_file: str, new_jobs_file: str, unwanted_jobs_file: str) -> None:
    import pandas as pd

    try:
        reviewed_jobs_df = pd.read_csv(reviewed_jobs_file)
    except Exception:
        reviewed_jobs_df = pd.DataFrame(columns=["title", "company"])

    new_jobs_df = pd.read_csv(new_jobs_file) if new_jobs_file else pd.DataFrame()
    #todo could fail here
    unwanted_jobs_df = pd.read_csv(unwanted_jobs_file)

    combined_df = pd.concat([reviewed_jobs_df, new_jobs_df, unwanted_jobs_df])
    combined_df.drop_duplicates(subset=["company", "title"], inplace=True)
    combined_df.to_csv(reviewed_jobs_file, index=False)

    added = len(new_jobs_df) + len(unwanted_jobs_df)
    print(f"Saved combined reviewed jobs to {reviewed_jobs_file} (added {added} entries)")

