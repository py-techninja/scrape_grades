import os
from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def login_and_scrape_grades():
    login_url = "https://sis-portal.uom.gr/login"
    grades_url = "https://sis-portal.uom.gr/student/grades/list_diploma"
    
    username = os.environ.get('USERNAME', 'dai18173')
    password = os.environ.get('PASSWORD', 'zei7!vo6')

    session = requests.Session()

    # Login
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': '_csrf'})['value']

    login_data = {
        'username': username,
        'password': password,
        '_csrf': csrf_token
    }
    session.post(login_url, data=login_data)

    # Fetch grades
    response = session.get(grades_url)
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

@app.route('/grades', methods=['GET'])
def get_grades():
    grades = login_and_scrape_grades()
    return jsonify(grades)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)