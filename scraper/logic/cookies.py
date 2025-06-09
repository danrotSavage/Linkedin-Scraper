import json


def load_cookies(driver, cookie_file_path):

    with open(cookie_file_path, "r") as f:
        cookies = json.load(f)

    driver.get("https://www.linkedin.com")  # Load base domain before setting cookies

    for cookie in cookies:
        # Clean up the cookie dict for Selenium
        cookie.pop("sameSite", None)
        cookie.pop("storeId", None)
        cookie.pop("hostOnly", None)
        cookie.pop("session", None)
        cookie.pop("id", None)
        driver.add_cookie(cookie)

    driver.get("https://www.linkedin.com/jobs")
