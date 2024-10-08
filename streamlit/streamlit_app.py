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
import plotly.express as px




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

### CALORIES CALCULATION
def calculate_daily_calories(user_info):
    # Extract user information
    age = user_info['age']
    gender = user_info['gender']
    weight = user_info['weight']  # in pounds
    height = user_info['height']  # in inches
    activity_level = user_info['activity_level']

    # Convert weight to kg and height to cm
    weight_kg = weight * 0.453592
    height_cm = height * 2.54

    # Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
    if gender.lower() == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Apply activity factor
    activity_factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very active': 1.9
    }
    
    activity_factor = activity_factors.get(activity_level.lower(), 1.2)
    
    # Calculate Total Daily Energy Expenditure (TDEE)
    tdee = bmr * activity_factor

    # Round to nearest 50 calories
    daily_calories = round(tdee / 50) * 50

    return daily_calories


def calculate_total_calories(food_entries):
    total_calories = 0
    protein_consumed = 0
    fat_consumed = 0
    carbs_consumed = 0
    for entry in food_entries:
        total_calories += entry.get('calories', 0)
        protein_consumed += entry.get('protein', 0)
        fat_consumed += entry.get('fat', 0)
        carbs_consumed += entry.get('carbs', 0)
    return total_calories, protein_consumed, fat_consumed, carbs_consumed

### CALORIES ENTRY



    
def calculate_calories_text(food_desc):
    with st.spinner('Estimating calories... Please wait.'):
        try:
            response = requests.post("http://127.0.0.1:5000/api/estimate_calories_from_text", json={"food_description": food_desc})
            if response.status_code == 200:
                st.success("Calorie estimation complete!")
                st.json(response.json())
                calorie_data = response.json()
                added_entry = add_calorie_entry(st.session_state.username,calorie_data)
                if added_entry:
                    st.session_state.food_info = get_food_info(st.session_state.username)
                    return True
                if not added_entry:
                    st.error("Unable to add calorie entry to database")
                    return False
            else:
                st.error("Unable to estimate calories")
                return False
        except:
            st.error("Unable to estimate calories")
            return False


def add_calorie_entry(username, json_data):

    food_name = json_data.get('food_name')
    calories = json_data.get('calories')
    protein = json_data.get('protein')
    fat = json_data.get('fat')
    carbs = json_data.get('carbs')
    additional_info = json_data.get('additional_info')
    response = requests.post("http://127.0.0.1:5000/api/add_calorie_entry", json={"username": username, "food_name": food_name, "calories": calories, "protein": protein, "fat": fat, \
                                                                                  "carbs": carbs, "additional_info": additional_info})
    if response.status_code == 200:
        st.success("Calorie entry added successfully!")
        return True
    else:
        st.error("Unable to add calorie entry")
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
                calorie_data = response.json()
                added_entry = add_calorie_entry(calorie_data)
            if added_entry:
                st.success("Calorie entry added to database successfully!")
                return True
            if not added_entry:
                st.error("Unable to add calorie entry to database")
                return False
            else:
                st.error(f"Failed to upload image. Status code: {response.status_code}")
                st.text(response.text)  # Display the error message from the server
        except requests.RequestException as e:
            st.error(f"An error occurred: {e}")
            return False
        



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
        calorie_goal = calculate_daily_calories(st.session_state.user_info)
        calories_consumed, protein_consumed, fat_consumed, carbs_consumed = calculate_total_calories(st.session_state.food_info)
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

        # Macronutrient breakdown
        st.subheader("Macronutrient Breakdown")
        
        # Calculate total macronutrients
        total_macros = protein_consumed + fat_consumed + carbs_consumed
        
        if total_macros > 0:
            # Prepare data for pie chart
            macro_data = {
                'Nutrient': ['Protein', 'Fat', 'Carbs'],
                'Grams': [protein_consumed, fat_consumed, carbs_consumed]
            }
            df_macros = pd.DataFrame(macro_data)

            # Create pie chart
            fig = px.pie(df_macros, values='Grams', names='Nutrient',
                         color='Nutrient',
                         color_discrete_map={'Protein': '#ff9999', 'Fat': '#66b3ff', 'Carbs': '#99ff99'})
            
            # Update layout for better readability
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(legend_title_text='Macronutrients')

            # Display the chart
            st.plotly_chart(fig)

            # Display macronutrient breakdown in text
            st.text(f"Protein: {protein_consumed:.1f}g")
            st.text(f"Fat: {fat_consumed:.1f}g")
            st.text(f"Carbs: {carbs_consumed:.1f}g")
        else:
            st.info("No macronutrient data available for the selected date.")

    # Add food intake form
    st.subheader("Add Food")
    food_desc = st.text_input("Use Food Description")
    uploaded_file = st.file_uploader("Use Food Image", type=["jpg", "jpeg", "png"])
    
    if st.button('Add Food'):
        ## If image uploaded use image, else use text
        if uploaded_file is not None:
        # Display the uploaded image
            food_img = Image.open(uploaded_file)
            st.image(food_img, caption='Uploaded Image', use_column_width=True)
            if food_img is not None:
                print("Using image to estimate calories")
                calculate_calories_image(uploaded_file)
        elif food_desc:
            print('Using food description to estimate calories')
            try:
                calculate_calories_text(food_desc)
            except:
                st.error(f"An error occurred while calculating calories")
    

    # Fetch and display recent food intake
    st.subheader("Food logged for the day")
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
    st.write(st.session_state.user_info)