from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
from vercel_kv import VercelKV

kv = VercelKV()

def get_grades():
    grades = kv.get('grades')
    last_update = kv.get('last_update')
    
    if grades and last_update:
        last_update = datetime.fromisoformat(last_update)
        if datetime.now() - last_update < timedelta(minutes=30):
            return json.loads(grades)
    
    return None

def set_grades(grades):
    kv.set('grades', json.dumps(grades))
    kv.set('last_update', datetime.now().isoformat())

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            grades = get_grades()
            
            if grades is None:
                self.send_response(202)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Grades are being updated. Please try again in a few minutes."}).encode('utf-8'))
                # Trigger background job to update grades
                os.system('vercel run api/update_grades.py')
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(grades, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_message = {"error": "Server error", "details": str(e)}
            self.wfile.write(json.dumps(error_message, ensure_ascii=False).encode('utf-8'))
        return