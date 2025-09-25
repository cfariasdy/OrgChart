# app.py (With Secure Login)

from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from functools import wraps
import csv
import sys
import os

# --- App Configuration ---
template_dir = os.path.join(os.path.abspath("."), 'templates')
app = Flask(__name__, template_folder=template_dir)
# IMPORTANT: Change this to a random string for production
app.config['SECRET_KEY'] = 'KayCow__EICSKeys__22022022__ReNNYY'
CORS(app)
bcrypt = Bcrypt(app)

# --- User Storage (In a real app, this would be a database) ---
# Replace the hash with the one you generated in step 2.
users = {
    "admin": {
        "password_hash": "$2b$12$AQOrN4tKhr7TU7Cbkh69g.VJjtpENrw8bRoRp8a4hUg9G1wmPrpP6"
    }
}


# --- Decorator for Requiring Login ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# --- New Login and Logout Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['user_id'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# --- Protected Org Chart Routes ---
@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/org-data')
@login_required
def get_org_data():
    csv_path = os.path.join(os.path.abspath("."), 'employee.csv')
    dept_data, error = create_departmental_charts(csv_path)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(dept_data)


# --- Unchanged Helper Functions ---
def create_departmental_charts(filepath):
    # ... (This entire function remains exactly the same) ...
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


if __name__ == '__main__':
    app.run(debug=True)