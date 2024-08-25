from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os

app = Flask(__name__)

def scrape_grades():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")  # Suppress console logs

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    grades = []
    try:
        # Login process
        # ... (keep the existing login code)

        # Scrape grades
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.odd, tr.even")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 4:
                grades.append({
                    "course_code": cols[0].get_attribute("title"),
                    "course_name": cols[1].get_attribute("title"),
                    "grade": cols[2].get_attribute("title"),
                    "semester": cols[3].get_attribute("title")
                })

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

    return grades

@app.route('/grades')
def get_grades():
    grades = scrape_grades()
    return jsonify(grades)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)