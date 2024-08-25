import requests
from bs4 import BeautifulSoup
import json
from vercel_kv import VercelKV

kv = VercelKV()

def login_and_scrape_grades():
    session = requests.Session()

    # Login
    login_url = "https://sis-portal.uom.gr/login"
    login_data = {
        "username": "dai18173",
        "password": "zei7!vo6",
        "loginButton": "είσοδος"
    }
    
    try:
        response = session.post(login_url, data=login_data)
        response.raise_for_status()
        
        # Check if login was successful
        if "logout" not in response.text:
            return {"error": "Login failed", "details": "Logout button not found on page"}
        
        # Scrape grades
        grades_url = "https://sis-portal.uom.gr/student/grades/list_diploma"
        response = session.get(grades_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        grades = []
        rows = soup.select("tr.odd, tr.even")
        
        if not rows:
            return {"error": "No grade data found", "details": "Could not find grade rows on the page"}
        
        for row in rows:
            cols = row.select("td")
            if len(cols) >= 4:
                grades.append({
                    "course_code": cols[0].get("title", ""),
                    "course_name": cols[1].get("title", ""),
                    "grade": cols[2].get("title", ""),
                    "semester": cols[3].get("title", "")
                })
        
        if not grades:
            return {"error": "No grades extracted", "details": "Found grade rows but couldn't extract data"}
        
        return grades
    
    except requests.RequestException as e:
        return {"error": "Network error", "details": str(e)}
    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}

def main():
    grades = login_and_scrape_grades()
    kv.set('grades', json.dumps(grades))
    kv.set('last_update', datetime.now().isoformat())
    print("Grades updated successfully")

if __name__ == "__main__":
    main()