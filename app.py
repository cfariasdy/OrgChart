# app.py (Deployment Version)

from flask import Flask, jsonify, render_template
from flask_cors import CORS
import csv
import sys
import os

# --- All your functions (resource_path, create_departmental_charts) and routes (@app.route) remain exactly the same ---
def resource_path(relative_path):
    # ... (no change) ...
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

template_dir = resource_path('templates')
app = Flask(__name__, template_folder=template_dir)
CORS(app)

def create_departmental_charts(filepath):
    # ... (no change) ...
    try:
        with open(filepath, mode='r', encoding='utf-8-sig') as file:
            employees = list(csv.DictReader(file))
    except FileNotFoundError:
        return None, f"CSV file not found at path: {filepath}. Please ensure it is bundled correctly."
    employee_map = {}
    for emp in employees:
        if not emp.get('id'):
            continue
        employee_map[emp['id']] = {
            'id': emp['id'],
            'firstName': emp.get('firstName', ''),
            'lastName': emp.get('LastName', ''),
            'title': emp.get('JobTitle', ''),
            'employmentStatus': emp.get('employmentStatus', ''),
            'location': emp.get('location', ''),
            'team': emp.get('department', ''),
            'children': []
        }
    all_nodes = list(employee_map.values())
    for node in all_nodes:
        emp_data = next((emp for emp in employees if emp.get('id') == node['id']), None)
        if not emp_data:
            continue
        supervisor_id = emp_data.get('supervisorId')
        if supervisor_id and supervisor_id in employee_map:
            employee_map[supervisor_id]['children'].append(node)
    department_charts = {}
    for node in all_nodes:
        department = node['team']
        if not department:
            continue
        emp_data = next((emp for emp in employees if emp.get('id') == node['id']), None)
        supervisor_id = emp_data.get('supervisorId')
        is_head = True
        if supervisor_id and supervisor_id in employee_map:
            supervisor_data = next((emp for emp in employees if emp.get('id') == supervisor_id), None)
            if supervisor_data and supervisor_data.get('department') == department:
                is_head = False
        if is_head:
            if department not in department_charts:
                department_charts[department] = []
            department_charts[department].append(node)
    final_charts = {}
    for dept, heads in department_charts.items():
        if len(heads) == 1:
            final_charts[dept] = heads[0]
        else:
            final_charts[dept] = {
                'firstName': dept,
                'lastName': 'Department',
                'title': 'All Members',
                'team': dept,
                'children': heads
            }
    return final_charts, None

@app.route('/org-data')
def get_org_data():
    # ... (no change) ...
    csv_path = resource_path('employee.csv')
    dept_data, error = create_departmental_charts(csv_path)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(dept_data)

@app.route('/')
def home():
    # ... (no change) ...
    return render_template('index.html')

# The if __name__ == '__main__': block is not needed for deployment,
# as the Gunicorn server will run the 'app' object directly.
# You can leave it in for continued local testing.
if __name__ == '__main__':
    app.run(debug=True) # Using debug=True for local testing is fine.