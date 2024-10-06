import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import random
import sqlite3
import os

# # Access secrets
# db_username = st.secrets["db_username"]
# db_password = st.secrets["db_password"]
# api_key = st.secrets["api_key"]

# # ## Connect to database
# if os.path.exists('../backend/instance/app.db'):
#     print("Database exists")
# else:
#     print("Database does not exist")
# conn = st.connection('../backend/instance/app.db', method='sql')
# df = conn.query('SELECT * FROM user')
# # print(df)

# Set page configuration



st.set_page_config(layout="wide")

# Mock data generation functions
def generate_mock_users():
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"}
    ]

def generate_mock_user_data(user_id, date):
    return {
        "weight": round(random.uniform(60, 80), 1),
        "calorie_goal": random.randint(1800, 2200),
        "calories_consumed": random.randint(1500, 2500)
    }

# Replace backend calls with mock data
def get_users():
    return generate_mock_users()

def get_user_data(user_id, date):
    return generate_mock_user_data(user_id, date)

# Sidebar for user selection and date
st.sidebar.title("Calorie Tracking App")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login Page")

    # Input fields for login
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    print(username, password)
    
    if st.button("Login"):
        print(username, password)
        response = requests.post("http://127.0.0.1:5000/api/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.success("Login successful!")
            st.session_state.logged_in = True
        else:
            st.error("Invalid username or password")
        

if st.session_state.logged_in:
    st.button('Log Out')
    st.session_state.logged_in = False
    users = get_users()
    # Date selection
    today = datetime.now().date()
    dates = [today - timedelta(days=i) for i in range(7)]
    selected_date = st.sidebar.selectbox("Select Date", dates, format_func=lambda x: x.strftime("%Y-%m-%d"))

    # Main content
    st.title(f"Calorie Tracker for Ajay")

    # Fetch user data
    #user_data = get_user_data(selected_user['id'], selected_date.strftime("%Y-%m-%d"))

    # Weight / Calories dropdown
    data_type = st.selectbox("Select Data Type", ["Calories", "Weight"])

    if data_type == "Weight":
        st.metric("Weight", f"{user_data.get('weight', 'N/A')} kg")
    else:
        # Calorie tracking
        calorie_goal = 2000 # user_data.get('calorie_goal', 2000)
        calories_consumed = 1500 # user_data.get('calories_consumed', 0)
        calories_remaining = max(0, calorie_goal - calories_consumed)

        col1, col2, col3 = st.columns(3)
        col1.metric("Calorie Goal", f"{calorie_goal} kcal")
        col2.metric("Calories Consumed", f"{calories_consumed} kcal")
        col3.metric("Calories Remaining", f"{calories_remaining} kcal")

        # Calorie progress bar
        st.progress(min(calories_consumed / calorie_goal, 1.0))

        # Calorie breakdown
        st.subheader("Calorie Breakdown")
        calorie_data = {
            "Category": ["Consumed", "Remaining"],
            "Calories": [calories_consumed, calories_remaining]
        }
        df = pd.DataFrame(calorie_data)
        st.bar_chart(df.set_index("Category"))

    # Add food intake form
    st.subheader("Add Food Intake")
    food_name = st.text_input("Food Name")
    calorie_amount = st.number_input("Calories", min_value=0)
    if st.button("Add Food"):
        # Here you would typically send a POST request to your backend to add the food intake
        st.success(f"Added {food_name} with {calorie_amount} calories")

    # Fetch and display recent food intake
    st.subheader("Recent Food Intake")
    response = requests.post("http://127.0.0.1:5000/api/get_food_day", json={"date": selected_date.strftime("%Y-%m-%d")})
    if response.status_code == 200:
        food_today = response.json()
        for food in food_today:
            st.text(f"{food['food_name']} - {food['calories']} calories")
    else:
        st.error("Failed to fetch recent food intake")


    # Display recent food intake
    st.subheader("Recent Food Intake")
    # Here you would fetch and display recent food intake from your backend
    # For demonstration, we'll use dummy data
    recent_intake = [
        {"name": "Apple", "calories": 95},
        {"name": "Chicken Sandwich", "calories": 350},
        {"name": "Salad", "calories": 200}
    ]
    for food in recent_intake:
        st.text(f"{food['name']} - {food['calories']} calories")
