import pandas as pd


def combine_jobs(reviewed_jobs_file, new_jobs_file):
    # Load the reviewed jobs DataFrame
    try:
        reviewed_jobs_df = pd.read_csv("reviewed_jobs.csv")
    except Exception  as e:
        columns = ['title','company']
        reviewed_jobs_df = pd.DataFrame(columns=columns)

    # Load the new jobs DataFrame
    new_jobs_df = pd.read_csv(new_jobs_file)

    # Combine the DataFrames
    combined_df = pd.concat([reviewed_jobs_df, new_jobs_df]).drop_duplicates(subset=['company', 'title'])

    # Save the combined DataFrame to a new CSV file
    combined_df.to_csv(reviewed_jobs_file, index=False)

    print(f"Combined DataFrame has been saved to '{reviewed_jobs_file}'.")


# File paths
reviewed_jobs_file = 'reviewed_jobs.csv'
new_jobs_file = 'new_jobs.csv'

# Combine the jobs DataFrames and save to a file
combine_jobs(reviewed_jobs_file, new_jobs_file)