import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import datetime
import matplotlib.pyplot as plt
import random
from geopy.distance import geodesic
import geopy.distance
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import geopy.exc
import os
import pandas as pd
from dateutil import relativedelta
import numpy as np

def login():
    if st.session_state.get('logged_in'):
        return True

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if username == "admin" and password == "password":
            st.success("Login successful!")
            st.session_state.logged_in = True
            return True
        else:
            st.error("Invalid username or password.")
            return False
        
def logout():
    st.session_state.logged_in = False

def calculate_distance(lat1, lon1, lat2, lon2):
    coords1 = (lat1, lon1)
    coords2 = (lat2, lon2)
    distance = geodesic(coords1, coords2).kilometers
    return distance

def home():
    st.markdown("<h1 style='font-family: Arial, sans-serif; font-size: 50px;'>DISPATCH DASHBOARD</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-family: Arial, sans-serif;'>Welcome to DISPATCH!</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-family: Arial, sans-serif; color: #800000;'>DISPATCH:</p> <p style='font-family: Bahnschrift, sans-serif;'>An Android-based real-time tracking and monitoring system for civilian fire emergency report and firefighter fire emergency response with GPS utilizing Geo-hashing Algorithm</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-family: Arial, sans-serif; font-size: 10px; margin-top: 150px;'>Questions? email us on:</p> <p style='font-family: Arial, sans-serif; color: #FFA500; font-size: 10px;'>dispatchofficial@gmail.com</p>", unsafe_allow_html=True)

def data():
    st.markdown(
        """
        <style>
        table {
            font-size: 13px;
            font-family: Monospace;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("Data Page")
    st.write("Data retrieved from Database:")

    users_ref = db.reference('Users')
    firefighters_ref = db.reference('Firefighter')

    data_type = st.selectbox("Select Data Type", ["👤 Users", "🧯 Firefighters"], key="data_type")

    if data_type == "👤 Users":
        data_ref = users_ref
    elif data_type == "🧯 Firefighters":
        data_ref = firefighters_ref

    keys = list(data_ref.get().keys())
    selected_key = st.selectbox("Select a Key", keys, key="selected_key")

    if selected_key:
        selected_data = data_ref.child(selected_key).get()
        st.write("Selected", data_type[:-1], "Key:", selected_key)

        with st.expander("User Details"):
            full_name = selected_data['firstName'] + " " + selected_data['lastName']
            st.write("Full Name:", full_name)
            st.write("Email:", selected_data['email'])

            if data_type == "👤 Users":
                st.write("Address:", selected_data['address'])
                st.write("Phone:", selected_data['phone'])
            elif data_type == "🧯 Firefighters":
                st.write("Station Address:", selected_data['address'])
                st.write("Phone:", selected_data['phone'])
                st.write("Telephone:", selected_data['telephone'])
                if 'badge number' in selected_data:
                    st.write("Badge #:", selected_data['badge number'])
                else:
                    st.write("Badge #:", None)

    if 'verify' in selected_data:
        if selected_data['verify']:
            st.write("Verified: Yes", "(",selected_data['verify'],")")
        else:
            st.write("Verified: No", "(",selected_data['verify'],")")
    else:
        st.write("Verified:", "No")

    if 'blocked' in selected_data:
        st.write("Blocked:", selected_data['blocked'])
    else:
        st.write("Blocked:", False)

    if 'blocked' in selected_data:
        blocked = selected_data['blocked']
    else:
        blocked = False

    if 'verify' in selected_data:
        verify = selected_data['verify']
    else:
        verify = False

    col1, col2, col3 = st.columns([3,2,1])

    if blocked:
        block_button_text = "Unblock 🔓"
    else:
        block_button_text = "Block 🔒"

    with col3:
        if st.button(block_button_text, key="block_button"):
            if blocked:
                selected_data['blocked'] = False
                st.write("Blocked:", False)
                st.write("User data unblocked")
            else:
                selected_data['blocked'] = True
                st.write("Blocked:", True)
                st.write("User data blocked")

            data_ref.child(selected_key).set(selected_data)
            st.experimental_rerun()

    if verify:
        verify_button_text = "Invalidate ❌"
    else:
        verify_button_text = "Validate ✅"

    with col3:
        if st.button(verify_button_text, key="verify_button"):
            if verify:
                selected_data['verify'] = False
                st.write("Verified:", False)
                st.write("User data verified")
            else:
                selected_data['verify'] = True
                st.write("Verified:", True)
                st.write("User data removed verified")

            data_ref.child(selected_key).set(selected_data)
            st.experimental_rerun()

    report_data = selected_data.get('Report')

    if report_data and 'Reports' in report_data:
        report_data.pop('Reports')

    if data_type == "👤 Users":
        if report_data:
            st.write(data_type[:-1], "Report Data:")
            st.table(report_data)
        else:
            st.write("No report.")

        report_datalist = data_ref.child(selected_key).child('Report').get()

        if 'Report' in selected_data:

            time_stamp = data_ref.child(selected_key).child('Report').child('TimeStamp').get()

            firebase_time = datetime.fromtimestamp(time_stamp / 1000)

            time_diff = datetime.now() - firebase_time

            if time_diff > timedelta(minutes=30):
                if 'Location' in report_datalist:
                    data_ref.child(selected_key).child('Report').child('Location').delete()

                get_verify = report_datalist['verified']
                if get_verify:
                    report_datalist['verified'] = False
                    data_ref.child(selected_key).child('Report').set(report_datalist)
                    st.experimental_rerun()

            if 'verified' in report_datalist:
                st.write("Verified:", report_datalist['verified'])
            else:
                st.write("Verified:", False)

            if 'verified' in report_datalist:
                verified = report_datalist['verified']
            else:
                verified = False

            if verified:
                verified_button_text = "Invalidate ❌"
            else:
                verified_button_text = "Validate ✅"

            col1, col2, col3, col4 = st.columns([3,3,2,1])

            with col4:
                if st.button(verified_button_text, key="verified_button"):
                    if verified:
                        report_datalist['verified'] = False
                        st.write("Verified:", False)
                        st.write("Report data verified")
                    else:
                        report_datalist['verified'] = True
                        st.write("Verified:", True)
                        st.write("Report data removed verified")

                    data_ref.child(selected_key).child('Report').set(report_datalist)
                    st.experimental_rerun()

    if data_type == "👤 Users":
        reports_ref = data_ref.child(selected_key).child('Report').child('Reports')
        reports = reports_ref.get()
        if reports:
            st.write(data_type[:-1], "Report Data:")
            table_data = []
            for report_key, report_value in reports.items():
                row_data = [report_key]
                row_data.extend(report_value.values())
                table_data.append(row_data)

            headers = ['Report Key/s (user identification key/s)'] + list(reports[list(reports.keys())[0]].keys())
            table = [headers] + table_data
            st.table(table)

            delete_key = st.text_input("Enter the key to delete:")

            if st.button("Delete"):
                if delete_key in reports:
                    del reports[delete_key]
                    reports_ref.set(reports)

                    st.write("Deleted key:", delete_key, "at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    st.write("Please refresh to update data")
                else:
                    st.write("Invalid key. Please enter a valid key.")
        else:
            st.write("No reports available.")

    st.markdown("""
    <style>
    .refresh-button-container 
    {
        margin-top: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([3,3,2,1])

    with col4:
        refresh_button = st.button("Refresh ♻️", key="refresh_button")
        if refresh_button:
            st.experimental_rerun()


def reports():

    st.markdown("""<style>table { font-size: 10px; font-family: Monospace; }</style>""", unsafe_allow_html=True)
    
    st.title("📄 Reports")

    data_ref = db.reference('Data')
    data = data_ref.get()

    df = pd.DataFrame.from_dict(data, orient='index')

    df['Date & Time'] = pd.to_datetime(df['Date & Time'])

    time_range = st.selectbox("Select Time Range", ['Today', 'Last 3 Days', 'Last Week', 'This Month', 'Past Months'])

    today = datetime.now().date()
    
    if time_range == 'Today':
        start_date = today
        end_date = today + timedelta(days=1)
    elif time_range == 'Last 3 Days':
        start_date = today - timedelta(days=3)
        end_date = today + timedelta(days=1)
    elif time_range == 'Last Week':
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = today - timedelta(days=today.weekday())
    elif time_range == 'This Month':
        start_date = today.replace(day=1)
        end_date = today + timedelta(days=1)
    elif time_range == 'Past Months':
        num_months = st.number_input('Select Number of Past Months', min_value=1, max_value=12, value=1)
        start_date = today - relativedelta.relativedelta(months=num_months)
        end_date = today

    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.min.time())

    filtered_df = df[(df['Date & Time'] >= start_datetime) & (df['Date & Time'] < end_datetime)]

    st.table(filtered_df)

    refresh_button = st.button("\U0001F504 Refresh", key="refresh_button")
    if refresh_button:
        st.experimental_rerun()    

def statistics():
    st.title("📈 Statistics")
    st.markdown("This page provides data analytics on location statistics, including NCR cities' occurrences and monthly trends.")

    data_ref = db.reference('Data')
    data = data_ref.get()

    NCR_cities = ['Manila', 'Pasay', 'Makati', 'Caloocan', 'Quezon', 'Taguig',
                  'Valenzuela', 'Malabon', 'Navotas', 'Marikina', 'Parañaque',
                  'Las Piñas', 'Mandaluyong', 'San Juan']

    city_counts = {city: 0 for city in NCR_cities}
    month_counts = {month: 0 for month in range(1, 13)}

    total_locations = 0
    total_date_time = 0

    for value in data.values():
        location = value.get('Location')
        date_time = value.get('Date & Time')
        if location:
            if 'Metro Manila' in location:
                location = location.replace('Metro Manila', '').strip()
            total_locations += 1
            for city in NCR_cities:
                if city.lower() in location.lower():
                    city_counts[city] += 1
                    break

        if date_time:
            total_date_time += 1
            dt = datetime.strptime(date_time, "%Y/%m/%d %H:%M:%S")
            month = dt.month
            month_counts[month] += 1

    cities = list(city_counts.keys())
    city_counts = list(city_counts.values())
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    month_counts = list(month_counts.values())

    total_count = sum(city_counts)

    graph_type = st.session_state.get("graph_type", "line")
    
    if graph_type == "line":
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        ax1.plot(cities, city_counts, marker='o', linestyle='-', color='blue')
        ax2.plot(months, month_counts, marker='o', linestyle='-', color='green')
    else:
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        ax1.bar(cities, city_counts, color='blue')
        ax2.bar(months, month_counts, color='green')

    ax1.set_xlabel('City')
    ax1.set_ylabel('Occurrences')
    ax1.set_title('Location Statistics (NCR Cities)')

    for i, count in enumerate(city_counts):
        ax1.text(i, count, str(count), ha='center', va='bottom')

    ax1.set_xticklabels(cities, rotation=90, ha='right')

    ax2.set_xlabel('Month')
    ax2.set_ylabel('Occurrences')
    ax2.set_title('Location Statistics by Month')

    for i, count in enumerate(month_counts):
        ax2.text(i, count, str(count), ha='center', va='bottom')

    ax2.set_xticklabels(months, rotation=90, ha='right')

    ax3.set_title('Next Occurrence Prediction')
    next_month = months[month_counts.index(max(month_counts)) % 12]
    next_city_index = np.argmax(city_counts)
    next_city = cities[next_city_index]
    prediction_labels = ['Next Month', f'Next City ({next_city})']
    prediction_sizes = [max(month_counts), city_counts[next_city_index]]
    ax3.pie(prediction_sizes, labels=prediction_labels, autopct='%1.1f%%')

    plt.xticks(rotation=90, ha='right')
    plt.tight_layout()

    st.pyplot(fig)

    col1, col2, col3, col4 = st.columns([3,3,2,1])

    toggle_button_text = "\U0001F4CA Switch to Bar Graph" if st.session_state.get("graph_type", "line") == "line" else "\U0001F4CA Switch to Line Graph"

    with col1:
        if st.button(toggle_button_text, key="toggle_button"):
            graph_type = st.session_state.get("graph_type", "line")
            if graph_type == "line":
                st.session_state["graph_type"] = "bar"
            else:
                st.session_state["graph_type"] = "line"
            st.experimental_rerun()
    with col4:
        refresh_button = st.button("\U0001F504 Refresh", key="refresh_button")
        if refresh_button:
            st.experimental_rerun()


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    local_css("style.css")

    st.markdown('<style>.sidebar { position: fixed; top: 0; left: 0; bottom: 0; width: 200px; padding: 20px; background-color: #f5f5f5; }</style>', unsafe_allow_html=True)
    st.markdown('<style>.sidebar .sidebar-content { margin-bottom: 20px; }</style>', unsafe_allow_html=True)

    nav_options = {
        "Home": home,
        "Data": data,
        "Reports": reports,
        "Statistics": statistics
    }

    st.sidebar.title("DISP👨‍🚒TCH")

    st.sidebar.markdown("## Navigation")


    if "selected_option" not in st.session_state:
        st.session_state.selected_option = "Home"

    home_clicked = st.sidebar.button("🏠 Home")
    if home_clicked:
        st.session_state.selected_option = "Home"

    data_clicked = st.sidebar.button("📊 Data")
    if data_clicked:
        st.session_state.selected_option = "Data"

    reports_clicked = st.sidebar.button("📄 Reports")
    if reports_clicked:
        st.session_state.selected_option = "Reports"

    statistics_clicked = st.sidebar.button("📈 Statistics")
    if statistics_clicked:
        st.session_state.selected_option = "Statistics"

    st.sidebar.markdown("## Account")

    if "Logout" not in st.session_state:
        st.session_state.Logout = False

    logout_clicked = st.sidebar.button("Log Out", help='Log Out')
    if logout_clicked:
        st.session_state.Logout = True
        st.experimental_rerun()

    if not st.session_state.Logout:
        nav_options[st.session_state.selected_option]()
        
def set():
    json_file_path = "JSON/dispatchmain-22ce5-firebase-adminsdk-xdm0a-668347f78c.json"

    if os.path.isfile(json_file_path):
        try:
            firebase_app = firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate(json_file_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://dispatchmain-22ce5-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
    else:
        st.error("JSON file not found at the specified path: " + json_file_path)
        firebase_app = firebase_admin.get_app()

    if login():
        main()


st.set_page_config(page_title="DISPATCH Dashboard", layout="wide")

set()