import os
import sys
import logging
from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Configure logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

def login_and_scrape_grades():
    login_url = "https://sis-portal.uom.gr/login"
    grades_url = "https://sis-portal.uom.gr/student/grades/list_diploma"
    
    username = os.environ.get('USERNAME', 'dai18173')
    password = os.environ.get('PASSWORD', 'zei7!vo6')

    session = requests.Session()

    try:
        # Login
        response = session.get(login_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': '_csrf'})['value']

        login_data = {
            'username': username,
            'password': password,
            '_csrf': csrf_token
        }
        response = session.post(login_url, data=login_data)
        response.raise_for_status()

        # Fetch grades
        response = session.get(grades_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        grades = []
        rows = soup.select('tr.odd, tr.even')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                grades.append({
                    "course_code": cols[0].get('title'),
                    "course_name": cols[1].get('title'),
                    "grade": cols[2].get('title'),
                    "semester": cols[3].get('title')
                })

        return grades

    except requests.RequestException as e:
        app.logger.error(f"Request error: {str(e)}")
        return {"error": "Failed to fetch grades. Please try again later."}
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return {"error": "An unexpected error occurred. Please try again later."}

@app.route('/')
def home():
    return "Welcome to the Grades API. Use /grades to fetch grades."

@app.route('/grades', methods=['GET'])
def get_grades():
    grades = login_and_scrape_grades()
    return jsonify(grades)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)