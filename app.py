from flask import Flask, render_template, request, redirect, url_for, session
from flask import Flask, render_template, request, flash, redirect, url_for
from flask import Flask, render_template, request, redirect, url_for
from flask import Flask,send_from_directory,render_template

from flask_restful import Resource, Api
from package.patient import Patients, Patient
from package.doctor import Doctors, Doctor
from package.appointment import Appointments, Appointment
from package.common import Common
from flask import jsonify
import threading
from threading import Lock
import json
import sqlite3
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
app = Flask(__name__, template_folder='templates')
app.secret_key = "c8ca6d07a4c0e699ec14d7ae742c9e24"

with open('config.json') as data_file:
    config = json.load(data_file)

db_lock = Lock()
def some_function():
    # Acquire the lock before accessing the database
    with db_lock:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()




def is_patient_logged_in():
    # Check if the 'patient_id' key exists in the session
    # This is a simplified example; you should adapt it to your actual authentication logic
    return 'patient_id' in session
# Define routes and initialize the database


def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create the admins table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL
                    )''')



    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Admin Registration Route
@app.route('/admin_register', methods=['GET', 'POST'])
@app.route('/submit_admin_registration', methods=['GET', 'POST'])
def admin_register():
    print("admin_register route called")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"Received username: {username}")
        print(f"Received password: {password}")

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
        else:
            # Insert the new admin into the database
            cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('admin_landing'))

    return render_template('admin/admin_register.html')

# Admin Login Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if the username and password match in the database
        cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()

        conn.close()

        if admin:
            flash('Login successful!', 'success')
            print(f"Login successful for user: {username}")
            return render_template('index.html')
        else:
            flash('Login failed. Please check your username and password.', 'error')

    return render_template('admin/admin_login.html')


def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create the doctors table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS doctors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        name TEXT NOT NULL,
                        specialization NOT NULL
                    )''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()


# Doctor Registration Route
@app.route('/doctor_register', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        specialization = request.form.get('specialization')

        # Open a connection and create a cursor
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:
            # Check if the username already exists
            cursor.execute("SELECT * FROM doctors WHERE username = ?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Username already exists. Please choose a different one.', 'error')
            else:
                # Insert the new doctor into the database
                cursor.execute("INSERT INTO doctors (name, username, password, specialization) VALUES (?, ?, ?, ?)",
                               (name, username, password, specialization))
                conn.commit()
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('doctor_login'))

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')

        finally:
            # Close the connection, whether there was an error or not
            conn.close()

    return render_template('Doctor/Doctor_register.html')




# Doctor Login Route
@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # Check if the username and password match in the database
        cursor.execute("SELECT * FROM doctors WHERE username = ? AND password = ?", (username, password))
        doctor = cursor.fetchone()

        conn.close()

        if doctor:
            flash('Login successful!', 'success')
            session['doctor_username'] = doctor[1]  # Store the doctor's username in the session
            return redirect(url_for('doctor_dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'error')

    return render_template('doctor/doctor_login.html')






def is_doctor_logged_in():
    # Check if the doctor is logged in (You can implement your logic here)
    return True

def get_logged_in_doctor_username():
    return session.get('doctor_username')


@app.route('/doctor_dashboard')
def doctor_dashboard():
    if is_doctor_logged_in():
        username = get_logged_in_doctor_username()  # Get the doctor's username (name)
        return render_template('Doctor/Doctor_dashboard.html', username=username)
    else:
        return redirect(url_for('doctor_login'))





# Create a route to fetch all doctors' names and passwords

@app.route('/get_all_doctors', methods=['GET'])
def get_all_doctors():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Query the database to fetch all doctors' names, passwords, and specializations
        cursor.execute("SELECT name, password, specialization FROM doctors")
        doctors_data = cursor.fetchall()

        # Convert the fetched data to a list of dictionaries
        doctor_list = [{"name": row[0], "password": row[1], "specialization": row[2]} for row in doctors_data]

        return jsonify(doctor_list)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        conn.close()





# Initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create the patients table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        password TEXT NOT NULL,
                        symptoms TEXT
                    )''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Patient Registration Route
@app.route('/patient', methods=['GET', 'POST'])
def patient_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        symptoms = request.form.get('symptoms')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if the email already exists
        cursor.execute("SELECT * FROM patients WHERE email = ?", (email,))
        existing_patient = cursor.fetchone()

        if existing_patient:
            flash('Email already exists. Please choose a different one.', 'error')
        else:
            # Insert the new patient into the database
            cursor.execute("INSERT INTO patients (name, email, password, symptoms) VALUES (?, ?, ?, ?)",
                           (name, email, password, symptoms))
            conn.commit()
            conn.close()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('patient_login'))

    return render_template('Patient/Patient_register.html')



# Patient Login Route
@app.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if a patient with the given email and password exists
        cursor.execute("SELECT * FROM patients WHERE email = ? AND password = ?", (email, password))
        patient = cursor.fetchone()

        conn.close()

        if patient:
            # Log in the patient and store their information in a session
            session['patient_id'] = patient[0]
            session['patient_name'] = patient[1]
            flash('Login successful!', 'success')
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('Patient/Patient_login.html')



# Create a route to fetch registered patients' data
@app.route('/get_registered_patients', methods=['GET'])
def get_registered_patients():
    try:
        conn = sqlite3.connect('database.db')
       # conn = connect_db()
        cursor = conn.cursor()

        # Query the database to fetch registered patients' details
        cursor.execute("SELECT name, email, password, symptoms FROM patients")
        patients_data = cursor.fetchall()

        # Convert the fetched data to a list of dictionaries
        patient_list = [{"name": row[0], "email": row[1], "password": row[2], "symptoms": row[3]} for row in patients_data]

        return jsonify(patient_list)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        conn.close()




def get_appointment_status(patient_id):

    appointment_status = "Not Book"
    return appointment_status

DEFAULT_APPOINTMENT_STATUS = ""


# Patient Dashboard Route
@app.route('/patient_dashboard')
def patient_dashboard():

    if not is_patient_logged_in():
        return redirect(url_for('patient_login'))  # Redirect to the login page if not logged in

    patient_id = session.get('patient_id')

    if patient_id is None:
        appointment_status = DEFAULT_APPOINTMENT_STATUS
    else:

        appointment_status = get_appointment_status(patient_id)

    return render_template('Patient/Patient_dashboard.html', appointment_status=appointment_status)

#book appointment route
def create_appointments_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            patient_name TEXT,
            symptoms TEXT
            doctor_name TEXT,
            specialization TEXT,
            appointment_date DATE
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/book_appointment')
def book_appointment():
    return render_template('patient/book_appointment.html')

# Route to display and book appointments
@app.route('/get_registered_doctors', methods=['GET'])
def get_registered_doctors():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, specialization FROM doctors")
    doctors = cursor.fetchall()
    conn.close()

    # Convert the list of doctors to a list of dictionaries for a more structured response
    doctor_list = [{'id': row[0], 'name': row[1], 'specialization': row[2] if row[2] else 'General'} for row in doctors]

    return doctor_list

#book now
from datetime import datetime



data = {
    "FrequentUrination Fatigue SlowWoundHealing": "Insulin",
    "Wheezing ChestTightness Coughing ShortnessOfBreath IncreasedMucusProduction": "Asthma Inhaler",
    "Headache Dizziness Chest Pain Shortness Of Breath Blurred Vision Excessive Thirst": "Heart Medication",
    "Fever Cough SoreThroat": "Cough Syrup",
}

# Data for machine learning
X = list(data.keys())
y = list(data.values())

# Create a TfidfVectorizer to convert symptom descriptions into numerical features
tfidf_vectorizer = TfidfVectorizer()
X_tfidf = tfidf_vectorizer.fit_transform(X)

# Create a decision tree classifier
clf = DecisionTreeClassifier()
clf.fit(X_tfidf, y)

@app.route('/book_now', methods=['POST'])
def book_now():
    data = request.get_json()
    doctor_name = data.get('doctorName')
    patient_name = data.get('patientName')
    symptoms = data.get('symptoms')  # This will be a list of selected symptoms

    # Get the current date and time
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Extract the doctor's name and specialization
    doctor_parts = doctor_name.split(' - ')
    doctor_name = doctor_parts[0]

    symptoms_string = symptoms

    # Convert the selected symptom descriptions into numerical features using TfidfVectorizer
    symptoms_tfidf = tfidf_vectorizer.transform([symptoms_string])

    # Predict medicine using the machine learning model
    predicted_medicine = clf.predict(symptoms_tfidf)[0]

    # Database operation: Insert the appointment details into the appointments table
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (patient_name, symptoms, doctor_name, appointment_date, recommended_medicine) VALUES (?, ?, ?, ?, ?)",
        (patient_name, symptoms_string, doctor_name, current_date, predicted_medicine))
    conn.commit()
    conn.close()
    result = {
        "success": True,
        "recommendedMedicine": predicted_medicine
    }

    return jsonify(result)


@app.route('/get_available_appointments', methods=['GET'])
def get_available_appointments():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Query the database to fetch available appointments' details along with disease and recommended medicine
        cursor.execute(
            "SELECT patient_name, symptoms, doctor_name, appointment_date, disease, recommended_medicine FROM appointments"
        )
        appointments_data = cursor.fetchall()

        # Convert the fetched data to a list of dictionaries
        appointment_list = [{
            "patient_name": row[0],
            "symptoms": row[1],
            "doctor_name": row[2],
            "appointment_date": row[3],
            "disease": row[4],
            "recommended_medicine": row[5]
        } for row in appointments_data]

        return jsonify(appointment_list)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        conn.close()



@app.route('/available_appointments', methods=['GET'])
def available_appointments():
    doctor_name = request.args.get('doctor_name')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE doctor_name = ?", (doctor_name,))
    appointments = cursor.fetchall()
    conn.close()
    return render_template('patient/available_appointments.html', doctor_name=doctor_name, appointments=appointments)


# Admin Landing Page Route
@app.route('/admin')
def admin_landing():
    return render_template('admin/admin_landing.html')

# Index Page Route
@app.route('/index')
def index_page():
    return render_template('index.html')



# all login out
@app.route('/doctor_logout')
def doctor_logout():
    session.pop('user', None)
    return render_template('doctor/doctor_logout.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('admin/logout.html')


@app.route('/patient_logout')
def patient():
    session.pop('user', None)
    return render_template('patient/patient_logout.html')

# Doctor Registration Page Route
@app.route('/Doctor')
def register_doctor():
    return render_template('Doctor/Doctor_register.html')




# Landing Page Route
@app.route('/')
def landing():
    return app.send_static_file('landing.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host=config['host'], port=config['port'])