import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import random
import sqlite3
import os
import streamlit as st
import requests
from PIL import Image
import io
from flask import jsonify




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

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


st.set_page_config(layout="wide")


### LOGIN FUNCTIONALITY
def login(username, password):

    response = requests.post("http://127.0.0.1:5000/api/login", json={"username": username, "password": password})
    if response.status_code == 200:
        st.success("Login successful!")
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.user_info = get_user_info(username)
        st.session_state.food_info = get_food_info(username)
        st.experimental_rerun()
    else:
        st.error("Invalid username or password")
        return False

def logout():
    st.session_state.logged_in = False
    if 'username' in st.session_state:
        del st.session_state.username
    st.experimental_rerun()

### DATABASE RETRIEVAL FUNCTIONS
def get_user_info(username):
    response = requests.post("http://127.0.0.1:5000/api/user_from_username", json={"username": username})
    if response.status_code == 200:
        return response.json()
    else:
        return response.json()
    
def get_food_info(username):
    response = requests.post("http://127.0.0.1:5000/api/food_by_username", json={"username": username})
    if response.status_code == 200:
        return response.json()
    else:
        return response.json()

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

def show_login_page():
    st.title("Login Page")

    # Input fields for login
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        login(username, password)

#### Calculate calories 
# def calculate_calories_image():
#     response = requests.post("http://127.0.0.1:5000/api/estimate_calories_from_image", json={"username": username, "password": password})
#     if response.status_code == 200:
#         st.success("Login successful!")
#         st.session_state.logged_in = True
#         return True
#     else:
#         st.error("Invalid username or password")
#         return False
    
def calculate_calories_text(food_desc):
    response = requests.post("http://127.0.0.1:5000/api/estimate_calories_from_text", json={"food_description": food_desc})
    if response.status_code == 200:
        st.success("Calorie estimation complete!")
        st.json(response.json())
        return True
    else:
        st.error("Unable to estimate calories")
        return False

def calculate_calories_image(uploaded_file):
    files = {
        'image': ('image.jpg', uploaded_file.getvalue(), 'image/jpeg')
    }

    # Make the POST request
    with st.spinner('Estimating calories... Please wait.'):
        try:
            response = requests.post('http://127.0.0.1:5000/api/estimate_calories_from_image', files=files)
            if response.status_code == 200:
                st.success("Calorie estimation complete!")
                st.json(response.json())  # Display the response from the server
            else:
                st.error(f"Failed to upload image. Status code: {response.status_code}")
                st.text(response.text)  # Display the error message from the server
        except requests.RequestException as e:
            st.error(f"An error occurred: {e}")

### App functionality

def show_main_app():
    if st.button('Log Out'):
        logout()
    ## Get most upto date database for food and user data
    
    users = get_users()
    # Date selection
    today = datetime.now().date()
    dates = [today - timedelta(days=i) for i in range(7)]
    selected_date = st.sidebar.selectbox("Select Date", dates, format_func=lambda x: x.strftime("%Y-%m-%d"))

    # Main content
    if st.session_state.logged_in:
        st.title(f"Calorie Tracker for {st.session_state.username}")

    # Fetch user data
    #user_data = get_user_data(selected_user['id'], selected_date.strftime("%Y-%m-%d"))

    # Weight / Calories dropdown
    data_type = st.selectbox("Select Data Type", ["Calories", "Weight History"])

    if data_type == "Weight History":
        st.metric("Weight")
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
    st.subheader("Add Food")
    food_desc = st.text_input("Use Food Description")
    uploaded_file = st.file_uploader("Use Food Image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # Display the uploaded image
        food_img = Image.open(uploaded_file)
        st.image(food_img, caption='Uploaded Image', use_column_width=True)
    if st.button('Add Food'):
        ## If image uploaded use image, else use text
        print(food_img)
        if food_img is not None:
            print("Using image to estimate calories")
            calculate_calories_image(uploaded_file)
        elif food_desc:
            print('Using food description to estimate calories')
            with st.spinner('Estimating calories... Please wait.'):
                    try:
                        calculate_calories_text(food_desc)
                    except:
                        st.error(f"An error occurred while calculating calories")
            

    # Fetch and display recent food intake
    st.subheader("Food logged for the day")
    response = requests.post("http://127.0.0.1:5000/api/get_food_day", json={"date": selected_date.strftime("%Y-%m-%d")})
    if response.status_code == 200:
        food_today = response.json()
        for food in food_today:
            st.text(f"{food['food_name']} - {food['calories']} calories")
    else:
        st.error("Failed to fetch recent food intake")


    # # Display recent food intake
    # st.subheader("Food Intake for the Day")
    # # Here you would fetch and display recent food intake from your backend
    # # For demonstration, we'll use dummy data
    # recent_intake = [
    #     {"name": "Apple", "calories": 95},
    #     {"name": "Chicken Sandwich", "calories": 350},
    #     {"name": "Salad", "calories": 200}
    # # ]
    # for food in recent_intake:
    #     st.text(f"{food['name']} - {food['calories']} calories")

    


if not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()
    st.write(st.session_state.food_info)