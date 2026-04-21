# import streamlit as st
# import pandas as pd
# import json
# import os

# FILE_NAME = "schedule.json"

# employees = ["Scott", "Bergen", "PB", "Williams", ]

# def load_data():
#     if os.path.exists(FILE_NAME):
#         with open(FILE_NAME, "r") as f:
#             return json.load(f)
#     return []

# def save_data(data):
#     with open(FILE_NAME, "w") as f:
#         json.dump(data, f, indent=4)

# def assign_shift(data, date, shift, employee):
#     for item in data:
#         if item["type"] == "shift" and item["date"] == str(date) and item["time"] == shift:
#             return False
#     data.append({
#         "type": "shift",
#         "date": str(date),
#         "time": shift,
#         "employee": employee,
#         "assigned_by": "Supervisor"
#     })
#     save_data(data)
#     return True

# def add_appointment(data, date, time, employee, appointment_type, notes):
#     data.append({
#         "type": "appointment",
#         "date": str(date),
#         "time": time,
#         "employee": employee,
#         "appointment_type": appointment_type,
#         "notes": notes
#     })
#     save_data(data)
#     return True

# st.title("Shift and Appointment Scheduler")

# data = load_data()

# # Supervisor shift assignment
# st.header("Supervisor Assign Shift")

# shift_date = st.date_input("Shift date")
# shift_time = st.selectbox("Shift", ["Morning", "Afternoon", "Night"])
# shift_employee = st.selectbox("Assign employee", employees)

# if st.button("Assign Shift"):
#     success = assign_shift(data, shift_date, shift_time, shift_employee)
#     if success:
#         st.success(f"{shift_employee} assigned to {shift_time} shift on {shift_date}")
#     else:
#         st.error("That shift is already assigned.")

# st.header("Employee Self-Assigned Appointment")

# appt_employee = st.selectbox("Employee name", employees, key="appt_employee")
# appt_date = st.date_input("Appointment date", key="appt_date")
# appt_time = st.text_input("Appointment time", placeholder="Example: 2:00 PM")
# appt_type = st.selectbox(
#     "Appointment type",
#     ["Doctor", "Meeting", "School", "Personal", "Other"],
#     key="appt_type"
# )
# appt_notes = st.text_area("Notes", key="appt_notes")

# if st.button("Add Appointment"):
#     add_appointment(data, appt_date, appt_time, appt_employee, appt_type, appt_notes)
#     st.success(f"Appointment added for {appt_employee}")

# st.header("All Schedule Entries")

# if data:
#     df = pd.DataFrame(data)
#     st.dataframe(df)
# else:
#     st.write("No entries yet.")

import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime, timedelta
import calendar

FILE_NAME = "schedule_calendar.json"

DEFAULT_EMPLOYEES = ["Alice", "Bob", "Carlos", "Diana"]
SHIFT_OPTIONS = {
    "Morning": ("08:00", "12:00"),
    "Afternoon": ("12:00", "16:00"),
    "Night": ("16:00", "20:00")
}


def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []


def save_data(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)


def ensure_state():
    if "data" not in st.session_state:
        st.session_state.data = load_data()
    if "employees" not in st.session_state:
        st.session_state.employees = DEFAULT_EMPLOYEES.copy()
    if "view_year" not in st.session_state:
        today = date.today()
        st.session_state.view_year = today.year
    if "view_month" not in st.session_state:
        st.session_state.view_month = today.month



def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M").time()



def overlaps(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)



def get_entries_for_day(data, selected_date):
    return [entry for entry in data if entry["date"] == str(selected_date)]



def has_conflict(data, employee, selected_date, start_time, end_time):
    new_start = parse_time(start_time)
    new_end = parse_time(end_time)

    for entry in data:
        if entry["employee"] != employee or entry["date"] != str(selected_date):
            continue

        existing_start = parse_time(entry["start_time"])
        existing_end = parse_time(entry["end_time"])

        if overlaps(new_start, new_end, existing_start, existing_end):
            return True, entry

    return False, None



def add_shift(selected_date, shift_name, employee):
    start_time, end_time = SHIFT_OPTIONS[shift_name]

    conflict, entry = has_conflict(
        st.session_state.data, employee, selected_date, start_time, end_time
    )
    if conflict:
        return False, f"Conflict with existing {entry['type']} from {entry['start_time']} to {entry['end_time']}"

    st.session_state.data.append({
        "type": "shift",
        "title": shift_name,
        "date": str(selected_date),
        "start_time": start_time,
        "end_time": end_time,
        "employee": employee,
        "details": "Assigned by supervisor"
    })
    save_data(st.session_state.data)
    return True, "Shift added"



def add_appointment(selected_date, employee, title, start_time, end_time, details):
    conflict, entry = has_conflict(
        st.session_state.data, employee, selected_date, start_time, end_time
    )
    if conflict:
        return False, f"Conflict with existing {entry['type']} from {entry['start_time']} to {entry['end_time']}"

    st.session_state.data.append({
        "type": "appointment",
        "title": title,
        "date": str(selected_date),
        "start_time": start_time,
        "end_time": end_time,
        "employee": employee,
        "details": details
    })
    save_data(st.session_state.data)
    return True, "Appointment added"



def delete_entry(index):
    st.session_state.data.pop(index)
    save_data(st.session_state.data)



def month_name(month_num):
    return calendar.month_name[month_num]



def previous_month():
    if st.session_state.view_month == 1:
        st.session_state.view_month = 12
        st.session_state.view_year -= 1
    else:
        st.session_state.view_month -= 1



def next_month():
    if st.session_state.view_month == 12:
        st.session_state.view_month = 1
        st.session_state.view_year += 1
    else:
        st.session_state.view_month += 1



def render_month_calendar(year, month, data):
    st.subheader(f"{month_name(month)} {year}")

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_cols = st.columns(7)
    for i, day in enumerate(days):
        day_cols[i].markdown(f"**{day}**")

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(year, month)

    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                in_month = day.month == month
                day_entries = get_entries_for_day(data, day)

                box_style = "padding:8px;border:1px solid #ccc;border-radius:8px;min-height:130px;"
                if not in_month:
                    st.markdown(f"<div style='{box_style};opacity:0.45'><b>{day.day}</b></div>", unsafe_allow_html=True)
                    continue

                lines = [f"<b>{day.day}</b>"]
                for entry in day_entries[:3]:
                    icon = "🟦" if entry["type"] == "shift" else "🟨"
                    lines.append(f"<div style='font-size:12px'>{icon} {entry['employee']} - {entry['title']}</div>")
                if len(day_entries) > 3:
                    lines.append(f"<div style='font-size:12px'>+{len(day_entries) - 3} more</div>")

                st.markdown(
                    f"<div style='{box_style}'>{''.join(lines)}</div>",
                    unsafe_allow_html=True
                )

                if st.button(f"Open {day}", key=f"open_{day}"):
                    st.session_state.selected_date = day



def main():
    st.set_page_config(page_title="Interactive Shift Calendar", layout="wide")
    ensure_state()

    st.title("Interactive Shift and Appointment Calendar")
    st.caption("Supervisors can assign shifts, and employees can add their own miscellaneous appointments.")

    if "selected_date" not in st.session_state:
        st.session_state.selected_date = date.today()

    with st.sidebar:
        st.header("Employees")
        new_employee = st.text_input("Add employee")
        if st.button("Add employee"):
            if new_employee.strip() and new_employee.strip() not in st.session_state.employees:
                st.session_state.employees.append(new_employee.strip())
                st.success(f"Added {new_employee.strip()}")
            else:
                st.warning("Enter a unique employee name.")

        st.divider()
        st.header("Calendar")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Prev"):
                previous_month()
        with col2:
            if st.button("Next →"):
                next_month()

        st.write(f"Viewing: {month_name(st.session_state.view_month)} {st.session_state.view_year}")

        manual_date = st.date_input("Jump to a date", value=st.session_state.selected_date)
        if manual_date != st.session_state.selected_date:
            st.session_state.selected_date = manual_date
            st.session_state.view_month = manual_date.month
            st.session_state.view_year = manual_date.year

    left, right = st.columns([2, 1])

    with left:
        render_month_calendar(
            st.session_state.view_year,
            st.session_state.view_month,
            st.session_state.data
        )

    with right:
        selected_date = st.session_state.selected_date
        st.subheader(f"Selected Date: {selected_date}")

        tab1, tab2, tab3 = st.tabs(["Assign Shift", "Add Appointment", "Day View"])

        with tab1:
            with st.form("shift_form"):
                employee = st.selectbox("Employee", st.session_state.employees)
                shift_name = st.selectbox("Shift", list(SHIFT_OPTIONS.keys()))
                submitted = st.form_submit_button("Assign shift")
                if submitted:
                    ok, msg = add_shift(selected_date, shift_name, employee)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab2:
            with st.form("appt_form"):
                employee = st.selectbox("Employee name", st.session_state.employees, key="appt_emp")
                title = st.text_input("Appointment title", placeholder="Doctor, school event, meeting...")
                start_time = st.time_input("Start time", value=datetime.strptime("09:00", "%H:%M").time())
                end_time = st.time_input("End time", value=datetime.strptime("10:00", "%H:%M").time())
                details = st.text_area("Details / notes")
                submitted = st.form_submit_button("Add appointment")

                if submitted:
                    if end_time <= start_time:
                        st.error("End time must be after start time.")
                    elif not title.strip():
                        st.error("Please enter an appointment title.")
                    else:
                        ok, msg = add_appointment(
                            selected_date,
                            employee,
                            title.strip(),
                            start_time.strftime("%H:%M"),
                            end_time.strftime("%H:%M"),
                            details.strip()
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        with tab3:
            day_entries = []
            for i, entry in enumerate(st.session_state.data):
                if entry["date"] == str(selected_date):
                    day_entries.append((i, entry))

            if not day_entries:
                st.info("No shifts or appointments on this day.")
            else:
                sorted_entries = sorted(day_entries, key=lambda x: x[1]["start_time"])
                for i, entry in sorted_entries:
                    entry_type = "Shift" if entry["type"] == "shift" else "Appointment"
                    with st.container(border=True):
                        st.markdown(f"**{entry_type}: {entry['title']}**")
                        st.write(f"Employee: {entry['employee']}")
                        st.write(f"Time: {entry['start_time']} - {entry['end_time']}")
                        if entry.get("details"):
                            st.write(f"Details: {entry['details']}")
                        if st.button("Delete", key=f"delete_{i}"):
                            delete_entry(i)
                            st.rerun()

    st.divider()
    st.subheader("All Entries")
    if st.session_state.data:
        df = pd.DataFrame(st.session_state.data)
        df = df[["date", "type", "title", "employee", "start_time", "end_time", "details"]]
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No schedule entries yet.")


if __name__ == "__main__":
    main()
