from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def login_and_scrape_grades():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")  # Suppress console logs

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Login process
        driver.get("https://sis-portal.uom.gr/login")
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys("dai18173")
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("zei7!vo6")
        login_button = driver.find_element(By.ID, "loginButton")
        login_button.click()

        # Wait for login to complete
        time.sleep(5)
        print("Login successful")

        # Navigate to grades page
        grades_url = "https://sis-portal.uom.gr/student/grades/list_diploma"
        driver.get(grades_url)
        time.sleep(5)

        # Check if we're on the correct page
        if "grades/list_diploma" not in driver.current_url:
            print("Not on the grades page. Attempting to navigate again.")
            driver.get(grades_url)
            time.sleep(5)

        # Wait for grade rows to be present
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr.odd, tr.even"))
            )
            print("Grades page loaded successfully")
        except:
            print("Could not load grades page")
            return

        # Scrape grades
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.odd, tr.even")
        grades = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 4:
                course_code = cols[0].get_attribute("title")
                course_name = cols[1].get_attribute("title")
                grade = cols[2].get_attribute("title")
                semester = cols[3].get_attribute("title")
                grades.append(f"{course_code} - {course_name}: {grade} ({semester})")

        print(f"Scraped {len(grades)} grades:")
        for grade in grades:
            print(grade)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    login_and_scrape_grades()