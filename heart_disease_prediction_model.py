

# 9


import pymysql
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import pickle

# Load the saved model
heart_model = pickle.load(open('C:/Users/HP/OneDrive/Desktop/heart disease model/heart_disease_model/heart_disease_model.sav', 'rb'))

# MySQL Database Connection
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='sqlpass',  # Replace with your actual MySQL password
        database='heartdb1',
        cursorclass=pymysql.cursors.DictCursor
    )

# Admin Login Page (dialog box behavior)
def admin_login():
    st.title("Admin Login")
    
    # Admin credentials check (assuming a table exists with the admin credentials)
    admin_username = st.text_input("Enter Admin Username")
    admin_password = st.text_input("Enter Admin Password", type='password')

    if st.button('Login'):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if admin credentials are correct
        cursor.execute("SELECT * FROM admin_credentials WHERE username = %s AND password = %s", (admin_username, admin_password))
        admin = cursor.fetchone()
        
        if admin:
            st.session_state.logged_in = True  # Set session state to indicate logged-in status
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")
        
        cursor.close()
        conn.close()

# Sidebar Navigation (only shows after login)
with st.sidebar:
    if "logged_in" in st.session_state and st.session_state.logged_in:
        selected = option_menu('Heart Disease Prediction System', ['Heart Disease Prediction', 'View Patient Data'], default_index=0)
    else:
        selected = None  # Hide menu if not logged in

# Main Content (Login and Prediction System)
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    # Show Login Form Before Logged In
    admin_login()
else:
    # 🏥 **Heart Disease Prediction Page**
    if selected == 'Heart Disease Prediction':
        st.title('Heart Disease Prediction Model')

        # Input fields
        col1, col2, col3 = st.columns(3)
        with col1: user_id = st.text_input('Enter Patient ID')
        with col2: user_name = st.text_input('Enter Patient Name')
        with col3: age = st.text_input('Enter Age')
        with col1: sex = st.text_input('Enter Sex (0 = Female, 1 = Male)')
        with col2: chest_pain = st.text_input('Enter Type of Chest Pain (0-3)')
        with col3: blood_pressure = st.text_input('Enter Resting Blood Pressure(100-200)')
        with col1: cholestrol = st.text_input('Enter Cholesterol(100-300)')
        with col2: blood_sugar = st.text_input('Enter Blood Sugar (0 or 1)')
        with col3: ECG = st.text_input('Enter ECG Results (0-2)')
        with col1: heart_rate = st.text_input('Enter Maximum Heart Rate Achieved(40-170)')
        with col2: angina = st.text_input('Enter Exercise-Induced Angina (0 or 1)')
        with col3: oldpeak = st.text_input('Enter ST Depression by Exercise(oldpeak)(0-6.2)')
        with col1: slope = st.text_input('Enter Slope of Peak Exercise ST Segment (0-2)')
        with col2: vessel_no = st.text_input('Enter Number of Major Vessels (0-3)')
        with col3: thal = st.text_input('Enter Type of Defect (0-3)')

        # Prediction
        heart_diagnosis = ''

        if st.button('Check Heart Disease'):
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if patient already exists
            cursor.execute("SELECT * FROM predictions WHERE user_id = %s", (user_id,))
            existing_patient = cursor.fetchone()

            if existing_patient:
                st.warning("⚠️ Patient data is already present in the database!")
            else:
                try:
                    # Convert input values to numeric types
                    age = int(age)
                    sex = int(sex)
                    chest_pain = int(chest_pain)
                    blood_pressure = int(blood_pressure)
                    cholestrol = int(cholestrol)
                    blood_sugar = int(blood_sugar)
                    ECG = int(ECG)
                    heart_rate = int(heart_rate)
                    angina = int(angina)
                    oldpeak = float(oldpeak)  # Oldpeak is usually a float
                    slope = int(slope)
                    vessel_no = int(vessel_no)
                    thal = int(thal)

                    # Make prediction
                    prediction = heart_model.predict([[age, sex, chest_pain, blood_pressure, cholestrol, blood_sugar, ECG, heart_rate, angina, oldpeak, slope, vessel_no, thal]])
                    heart_diagnosis = 'The person has a Heart Disease' if prediction[0] == 1 else 'The person does not have a Heart Disease'
                    st.success(heart_diagnosis)

                    # Store Data in MySQL
                    sql = """
                    INSERT INTO predictions (user_id, user_name, age, sex, chest_pain, blood_pressure, cholestrol, blood_sugar, ECG, heart_rate, angina, oldpeak, slope, vessel_no, thal, prediction_result)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (user_id, user_name, age, sex, chest_pain, blood_pressure, cholestrol, blood_sugar, ECG, heart_rate, angina, oldpeak, slope, vessel_no, thal, heart_diagnosis)
                    cursor.execute(sql, values)
                    conn.commit()
                    st.success("✅ Patient Data Saved Successfully!")

                except ValueError:
                    st.error("Invalid input! Please enter numeric values for all fields.")

            cursor.close()
            conn.close()

    # 📊 **View Patient Data Page**
    if selected == 'View Patient Data':
        st.title('Patient Data Records')

        if st.button('Load Patient Data'):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM predictions")
            data = cursor.fetchall()
            conn.close()

            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.warning("⚠️ No data found in the database!")



















