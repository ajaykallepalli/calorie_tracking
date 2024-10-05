import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import random

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

# User dropdown
users = get_users()
selected_user = st.sidebar.selectbox("Select User", users, format_func=lambda x: x['id'])

# Date selection
today = datetime.now().date()
dates = [today - timedelta(days=i) for i in range(7)]
selected_date = st.sidebar.selectbox("Select Date", dates, format_func=lambda x: x.strftime("%Y-%m-%d"))

# Main content
st.title(f"Calorie Tracker for {selected_user['name']}")

# Fetch user data
user_data = get_user_data(selected_user['id'], selected_date.strftime("%Y-%m-%d"))

# Weight / Calories dropdown
data_type = st.selectbox("Select Data Type", ["Weight", "Calories"])

if data_type == "Weight":
    st.metric("Weight", f"{user_data.get('weight', 'N/A')} kg")
else:
    # Calorie tracking
    calorie_goal = user_data.get('calorie_goal', 2000)
    calories_consumed = user_data.get('calories_consumed', 0)
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
