import logging

from pandas import DataFrame


def filter_by_company(company_name: str) -> bool:
    bad_companies = ["sqlink", "check point", "elbit", "rafael", "microsoft", "wix"]
    return any(c in company_name for c in bad_companies)

def filter_by_description(desc: str) -> bool:
    bad_substring = ["4+", "4 +", "5+", "5 +", "PHP", "5 years", "six years", "8+"]
    return any(b in desc for b in bad_substring)

def filter_by_title(title: str) -> bool:
    bad_substring = [
        "solutions", "data", "frontend", "remote", "react", "embedded", "qa", "devops", "android",
        "architect", "principal", "automation", "lead", "leader", "product", "business intelligence",
        "c++", "angular", "manager", "sr.", "support", "sre", "system", "sql", " ai ", "solution",
        "firmware", "ios ", "machine learning", "decsecops", "hardware", " it ", " go ",
        "artificial intelligence", "javascript", "++", "algorithm", "unity", "mobile", "sap", "idm",
        "account executive", " staff ", "infrastructure", "cobol",
    ]
    return any(b in title for b in bad_substring)

#if over 1 week
def filter_by_date(date_posted: str) -> bool:
    return "month" in date_posted or ("week" in date_posted and "1" not in date_posted)


def filter_by_location(location: str) -> bool:
    bad_locations = [
        "netanya", "modiin", "haifa", "remote", "hod hasharon", "petah tikva", "raanana", "yokneam",
        "yoqneam", "jerusalem", "rosh haayin", "rehovot", "ramat hasharon", "karmiel", "ahihud",
        "be'er sheva", "veer yaakov", "kfar saba", "omer", "south district", "afikim", "yakum",
        "migdal haemek", "north district",
    ]
    return any(b in location for b in bad_locations)

def filter_viewed_jobs(
    company: str, job_title: str, reviewed_jobs_df: DataFrame
) -> bool:
    global reviewed
    # if empty do not skip
    empty_df = not reviewed_jobs_df.query(
        "company == @company and title == @job_title"
    ).empty
    if empty_df:
        logging.info(f"---- skipping {job_title} from {company}")
        reviewed += 1
    return empty_df

















def clean_string(input_string: str) -> str:
    return input_string.replace("\n", " ").replace("Show more", "").strip()