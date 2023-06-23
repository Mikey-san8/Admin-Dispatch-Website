import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import datetime
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import geopy.distance
from geopy.geocoders import Nominatim
import time
from datetime import datetime, timedelta
import geopy.exc

def calculate_distance(lat1, lon1, lat2, lon2):

    coords1 = (lat1, lon1)
    coords2 = (lat2, lon2)
    distance = geodesic(coords1, coords2).kilometers
    return distance

try:
    firebase_app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("C:\Users\Joe Saludares\Documents\Jow\DISPATCH\JSON\dispatchmain-22ce5-firebase-adminsdk-xdm0a-668347f78c.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://dispatchmain-22ce5-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

    firebase_app = firebase_admin.get_app()

st.set_page_config(page_title="DISPATCH Dashboard")

nav_options = ["Home", "Data", "Statistics"]
nav_choice = st.sidebar.selectbox("Navigation", nav_options)

st.markdown(
    """
    <style>
    table {
        font-size: 10.5px;
    }
    button {
        float: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if nav_choice == "Home":
    st.markdown("<h1 style='font-family: Arial, sans-serif; font-size: 50px;'>DISPATCH DASHBOARD</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-family: Arial, sans-serif;'>Welcome to DISPATCH!</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-family: Arial, sans-serif; color: #800000;'>DISPATCH:</p> <p style='font-family: Bahnschrift, sans-serif;'>An Android-based real-time tracking and monitoring system for civilian fire emergency report and firefighter fire emergency response with GPS utilizing Geo-hashing Algorithm</p>", unsafe_allow_html=True)

elif nav_choice == "Data":
    st.title("Data Page")
    st.write("Data retrieved from Database:")

    users_ref = db.reference('Users')
    firefighters_ref = db.reference('Firefighter')

    data_type = st.sidebar.selectbox("Select Data Type", ["Users", "Firefighters"], key="data_type")

    if data_type == "Users":
        data_ref = users_ref
    elif data_type == "Firefighters":
        data_ref = firefighters_ref

    keys = list(data_ref.get().keys())
    selected_key = st.sidebar.selectbox("Select a Key", keys, key="selected_key")

    if selected_key:
        selected_data = data_ref.child(selected_key).get()
        st.write("Selected", data_type[:-1], "Key:", selected_key)

        with st.expander("User Details"):
            full_name = selected_data['firstName'] + " " + selected_data['lastName']
            st.write("Full Name:", full_name)
            st.write("Email:", selected_data['email'])

            if data_type == "Users":
                st.write("Address:", selected_data['address'])
                st.write("Phone:", selected_data['phone'])
            elif data_type == "Firefighters":
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

    if blocked:
        block_button_text = "Unblock"
    else:
        block_button_text = "Block"

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
        verify_button_text = "Invalidate"
    else:
        verify_button_text = "Validate"

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

    if data_type == "Users":
        if report_data:
            st.write(data_type[:-1], "Report Data:")
            st.table(report_data)
        else:
            st.write("No report.")
        
        report_datalist = data_ref.child(selected_key).child('Report').get()

        if 'Report' in selected_data:

            current_time = int(time.time() * 1000)    

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
                verified_button_text = "Invalidate"
            else:
                verified_button_text = "Validate"

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

    if data_type == "Users":
        reports_ref = data_ref.child(selected_key).child('Report').child('Reports')
        reports = reports_ref.get()
        if reports:
            st.write(data_type[:-1], "Report Data:")
            table_data = []
            for report_key, report_value in reports.items():
                row_data = [report_key]
                row_data.extend(report_value.values())
                table_data.append(row_data)

            headers = ["Report ID"] + list(reports[list(reports.keys())[0]].keys())
            table = [headers] + table_data
            st.table(table)

            st.write("Enter the key to delete:")
            delete_key = st.text_input("Key")

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

        refresh_button = st.button("Refresh", key="refresh_button")
        if refresh_button:
                st.experimental_rerun()     

elif nav_choice == "Statistics":

    data_ref = db.reference('Data')
    data = data_ref.get()

    locations = {}

    for key, value in data.items():
        location = value.get('Location')
        if location:
            if location in locations:
                locations[location] += 1
            else:
                locations[location] = 1

    st.title("Location Statistics")
    st.write("Occurrences of each location:")

    st.table([(location, count) for location, count in locations.items()])

    target_address = st.sidebar.text_input("Enter target address:", key="target_address")

    geolocator = Nominatim(user_agent="dispatch_dashboard")

    try:
        target_location = geolocator.geocode(target_address)
    except geopy.exc.GeocoderUnavailable:
        target_location = None
        st.sidebar.write("Geocoding service is currently unavailable. Please try again later.")
    
    if target_location:
        target_lat = target_location.latitude
        target_lon = target_location.longitude

        ncr_cities = {
        'Manila City': (14.5995, 120.9842),
        'Pasay City': (14.5378, 121.0014),
        'Makati City': (14.5547, 121.0244),
        'Caloocan City': (14.6492, 120.9849),
        'Las Pinas City': (14.4445, 120.9997),
        'Malabon City': (14.6694, 120.9653),
        'Mandaluyong City': (14.5794, 121.0359),
        'Marikina City': (14.6507, 121.1029),
        'Paranaque City': (14.4793, 121.0198),
        'Navotas City': (14.6667, 120.9416),
        'Pasig City': (14.5764, 121.0851),
        'Quezon City': (14.6760, 121.0437),
        'San Juan City': (14.6019, 121.0355),
        'Taguig City': (14.5176, 121.0509),
        'Valenzuela City': (14.6942, 120.9629)
        }

        city_distances = {}

        for city, city_coords in ncr_cities.items():
            distance = geopy.distance.geodesic(city_coords, (target_lat, target_lon)).kilometers
            city_distances[city] = distance

        nearest_city = min(city_distances, key=city_distances.get)
        nearest_distance = city_distances[nearest_city]

        st.sidebar.write("Nearest City:", nearest_city)
        st.sidebar.write("Distance:", nearest_distance, "km")
    else:
        if not target_address:
            st.sidebar.write("No address entered")
        else:
            st.sidebar.write("Invalid target address. Please enter a valid address.")
    
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
    counts = list(city_counts.values())

    total_count = sum(counts)

    fig, ax = plt.subplots()
    ax.barh(cities, counts)

    ax.set_xlabel('Occurrences')
    ax.set_ylabel('City')
    ax.set_title('Location Statistics (NCR Cities)')

    for i, count in enumerate(counts):
        ax.text(count, i, str(count), ha='left', va='center')

    ax.text(total_count + 10, len(cities) + 0.5, f'Total: {total_locations}', ha='right', va='center')

    plt.xticks(rotation=0)

    st.pyplot(fig)

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December']
    counts = list(month_counts.values())

    fig, ax = plt.subplots()
    ax.barh(months, counts)

    ax.set_xlabel('Occurrences')
    ax.set_ylabel('Month')
    ax.set_title('Location Statistics by Month')

    for i, count in enumerate(counts):
        ax.text(count, i, str(count), ha='left', va='center')

    plt.xticks(rotation=0)

    st.pyplot(fig)












