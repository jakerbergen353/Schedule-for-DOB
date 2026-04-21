import streamlit as st
import pandas as pd
import json
import os

FILE_NAME = "schedule.json"

employees = ["Scott", "Bergen", "PB", "Williams", ]

def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

def assign_shift(data, date, shift, employee):
    for item in data:
        if item["type"] == "shift" and item["date"] == str(date) and item["time"] == shift:
            return False
    data.append({
        "type": "shift",
        "date": str(date),
        "time": shift,
        "employee": employee,
        "assigned_by": "Supervisor"
    })
    save_data(data)
    return True

def add_appointment(data, date, time, employee, appointment_type, notes):
    data.append({
        "type": "appointment",
        "date": str(date),
        "time": time,
        "employee": employee,
        "appointment_type": appointment_type,
        "notes": notes
    })
    save_data(data)
    return True

st.title("Shift and Appointment Scheduler")

data = load_data()

# Supervisor shift assignment
st.header("Supervisor Assign Shift")

shift_date = st.date_input("Shift date")
shift_time = st.selectbox("Shift", ["Morning", "Afternoon", "Night"])
shift_employee = st.selectbox("Assign employee", employees)

if st.button("Assign Shift"):
    success = assign_shift(data, shift_date, shift_time, shift_employee)
    if success:
        st.success(f"{shift_employee} assigned to {shift_time} shift on {shift_date}")
    else:
        st.error("That shift is already assigned.")

st.header("Employee Self-Assigned Appointment")

appt_employee = st.selectbox("Employee name", employees, key="appt_employee")
appt_date = st.date_input("Appointment date", key="appt_date")
appt_time = st.text_input("Appointment time", placeholder="Example: 2:00 PM")
appt_type = st.selectbox(
    "Appointment type",
    ["Doctor", "Meeting", "School", "Personal", "Other"],
    key="appt_type"
)
appt_notes = st.text_area("Notes", key="appt_notes")

if st.button("Add Appointment"):
    add_appointment(data, appt_date, appt_time, appt_employee, appt_type, appt_notes)
    st.success(f"Appointment added for {appt_employee}")

st.header("All Schedule Entries")

if data:
    df = pd.DataFrame(data)
    st.dataframe(df)
else:
    st.write("No entries yet.")