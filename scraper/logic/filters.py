import logging

from pandas import DataFrame

logger = logging.getLogger(__name__)

# def filter_dec(func):
#     def wrapper(parameter, counter):
#         if (func(parameter)):
#             counter+=1
#             return True
#         return False

def filter_by_company(company_name: str) -> bool:
    bad_companies = ["sqlink", "check point", "elbit", "rafael", "microsoft", "wix", "amazon", "google"]
    return any(c in company_name for c in bad_companies)

def filter_by_description(desc: str) -> bool:
    bad_substring = [ "5+", "5 +", "PHP", "5 years", "six years", "8+", "6+", "7+", "c++", "6 years", "7 years"]
    return any(b in desc for b in bad_substring)

def filter_by_title(title: str) -> bool:
    bad_substring = [
        "solutions", "data", "frontend", "remote", "react", "embedded", "qa", "devops", "android",
        "architect", "principal", "automation", "lead", "leader", "product", "business intelligence",
        "c++", "angular", "manager", "support", "sre", "system", "sql", " ai ", "solution",
        "firmware", "ios ", "machine learning", "decsecops", "hardware", " it ", " go ",
        "artificial intelligence", "javascript", "++", "algorithm", "unity", "mobile", "sap", "idm",
        "account executive", " staff ", "cobol", "graduate",
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
        "migdal haemek", "north district", "herzliya", "san francisco", "san jose" , "italy", "india",
        "yakum",
    ]
    return any(b in location for b in bad_locations)


def filter_viewed_jobs(company: str, job_title: str, reviewed_jobs_df: DataFrame) -> bool:
    global rev
    # if job already found skip
    match_found  = not reviewed_jobs_df.query(
        "company == @company and title == @job_title"
    ).empty
    if match_found:
        logger.info(f"---- skipping {job_title} from {company}")
    return match_found
















def clean_string(input_string: str) -> str:
    return input_string.replace("\n", " ").replace("Show more", "").strip()