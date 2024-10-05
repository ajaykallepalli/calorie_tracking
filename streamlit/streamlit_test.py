import streamlit as st
import pandas as pd
from datetime import datetime

# Fake Data for demonstration
food_data = {
    'Date': [datetime.today().date()],
    'Food Item': ['Apple', 'Sandwich', 'Orange'],
    'Calories': [95, 300, 62]
}

exercise_data = {
    'Date': [datetime.today().date()],
    'Exercise': ['Running', 'Cycling'],
    'Calories Burned': [250, 180]
}

# Convert to DataFrame
food_df = pd.DataFrame(food_data)
exercise_df = pd.DataFrame(exercise_data)

# Streamlit App
st.title("MyFitnessPal Replica")

# Food Logging
st.header("Log Food Intake")
food_item = st.text_input("Food Item")
calories = st.number_input("Calories", min_value=0)

if st.button("Add Food"):
    new_food = {'Date': datetime.today().date(), 'Food Item': food_item, 'Calories': calories}
    food_df = pd.concat([food_df, pd.DataFrame([new_food])], ignore_index=True)
    st.success(f"Added {food_item} with {calories} calories.")

# Show Food Log
st.subheader("Food Log")
st.dataframe(food_df)

# Exercise Logging
st.header("Log Exercise")
exercise = st.text_input("Exercise")
calories_burned = st.number_input("Calories Burned", min_value=0, key="exercise")

if st.button("Add Exercise"):
    new_exercise = {'Date': datetime.today().date(), 'Exercise': exercise, 'Calories Burned': calories_burned}
    exercise_df = pd.concat([exercise_df, pd.DataFrame([new_exercise])], ignore_index=True)
    st.success(f"Added {exercise} with {calories_burned} calories burned.")

# Show Exercise Log
st.subheader("Exercise Log")
st.dataframe(exercise_df)

# Summary Dashboard
st.header("Daily Summary")

total_food_calories = food_df['Calories'].sum()
total_exercise_calories = exercise_df['Calories Burned'].sum()
net_calories = total_food_calories - total_exercise_calories

st.metric("Total Calories Consumed", total_food_calories)
st.metric("Total Calories Burned", total_exercise_calories)
st.metric("Net Calories", net_calories)
