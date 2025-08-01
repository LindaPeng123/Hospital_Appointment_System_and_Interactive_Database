import json
import sys
import requests
import datetime

DATABASE_URLS = {0: "https://hospital1-850e0-default-rtdb.firebaseio.com",
                 1: "https://hospital-2-f901a-default-rtdb.firebaseio.com",
                 2: "https://hospital-3-502e9-default-rtdb.firebaseio.com"}

# hash function: based on the ASCII
def hash_userId(userId):
    hash_value = sum(ord(char) for char in userId)
    return hash_value % 3


# auxiliary function 1: validate date format
def validate_date_format(date_string):
    try:
        if len(date_string) != 10 or date_string[4] != '-' or date_string[7] != '-':
            return False
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


# auxiliary function 2: validate time format
def validate_time_format(time_string):
    try:
        # Split the time string into hours and minutes
        hours, minutes = time_string.split(':')
        # Check if hours and minutes are two digits and within the valid range
        if len(hours) == 2 and len(minutes) == 2:
            if 0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59:
                return True
        return False
    except ValueError:
        return False


# auxiliary function 3: validate if userId exists
def check_user_exists(user_id):
    hash_value = hash_userId(user_id)
    database_url = DATABASE_URLS[hash_value]

    response = requests.get(database_url + "/users.json")

    if response.status_code == 200:
        users = response.json()

        if users:  # Check if users is not empty
            return user_id in users
        else:
            return False
    else:
        print("Failed to fetch users from the database.")
        return False


# auxiliary function 4: find scheduled times and output remaining available times
def find_reserved_times_by_date(date):
    # Define all available appointment times
    available_times = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00']

    # Get the reserved appointment times
    reserved_times = []
    for database_url in DATABASE_URLS.values():
        try:
            response = requests.get(database_url + "/appointments.json")
            response.raise_for_status()  # Raise an exception for HTTP errors

            if response.text.strip() == 'null':  # If response text is null, skip to the next database
                continue

            appointments = response.json()

            if not appointments:  # If appointments is empty, skip to the next database
                print("No appointments found in this database.")
                continue

            for appointment_data in appointments.values():
                if "date" in appointment_data:
                    if appointment_data["date"] == date:
                        time = appointment_data.get("time")
                        if time is None:
                            print("All available times can be reserved:")
                            print(available_times)
                            return available_times  # If appointment time is null, return all available times
                        else:
                            reserved_times.append(time)

        except requests.HTTPError as e:
            print("HTTP Error:", e)
        except Exception as e:
            print("Error occurred:", e)

    # Calculate remaining available times
    curr_available_times = [time for time in available_times if time not in reserved_times]
    if not curr_available_times:
        print("Today there are no remaining available appointment times.")
    else:
        print("Remaining available appointment times:")
        print(curr_available_times)
    return curr_available_times


# main function 1：find appointments by user
def find_appointments_by_user(user_id):
    user_exists = False
    for database_url in DATABASE_URLS.values():
        response = requests.get(database_url + "/users.json")
        if response.status_code == 200:
            users = response.json()
            if user_id in users:
                user_exists = True
                break

    if not user_exists:
        print("This user does not exist.")
        return {}

    hash_value = hash_userId(user_id)
    database_url = DATABASE_URLS[hash_value]
    response = requests.get(database_url + "/appointments.json")
    if response.status_code == 200:
        appointments = response.json()
        if appointments:
            found_appointments = {}
            print(f"Appointments for user {user_id}:")
            # Ensure there are appointments to sort and that they are filtered by user_id
            filtered_appointments = {k: v for k, v in appointments.items() if v["userId"] == user_id}
            if not filtered_appointments:
                print("No appointments found for this user.")
                return {}

            # Sort reservations by date and time using the sorted function
            sorted_appointments = sorted(filtered_appointments.items(), key=lambda x: (x[1]["date"], x[1]["time"]))
            for key, appointment in sorted_appointments:
                print(f"{appointment['date']} -- {appointment['time']} -- {appointment['reason']}")
                found_appointments[key] = appointment

            return found_appointments
        else:
            print("No appointment records found for this user.")
            return {}
    else:
        print("Failed to fetch appointments due to a network error.")
        return {}


# main function 2：find appointments by date
def find_appointments_by_date():
    while True:
        date = input("Enter date (YYYY-MM-DD): ")
        if validate_date_format(date):
            break
        else:
            print("Date error: Date format should be 'YYYY-MM-DD'. Please enter again.")

    found_appointments = False  # initialize the found_appointments variable
    for hash_value, database_url in DATABASE_URLS.items():
        response = requests.get(database_url + "/appointments.json")
        if response.status_code == 200:
            appointments = response.json()
            if appointments:  # check if there are any reservation data
                # Sort appointments by time before processing
                sorted_appointments = sorted(appointments.values(), key=lambda x: x["time"])
                for appointment in sorted_appointments:
                    if appointment.get("date") == date:  # use the get method to handle possible cases where the key does not exist
                        print(f"{appointment.get('time')} -- {appointment.get('userId')} -- {appointment.get('reason')}")
                        found_appointments = True  # if a reservation is found, set found_appointments to True

    if not found_appointments:
        print("No appointments found for this date.")  # if no reservations are found, output a message


# main function 3: make an appointment
def make_appointment():
    while True:
        user_id = input("Enter user ID: ")
        hash_value = hash_userId(user_id)
        database_url = DATABASE_URLS[hash_value]

        if not check_user_exists(user_id):
            print("User not found.")
            retry = input("Do you want to re-enter user ID? (yes/no): ")
            if retry.lower() != "yes":
                return
            continue

        current_datetime = datetime.datetime.now()
        current_date = current_datetime.date()
        current_time = current_datetime.time()

        while True:
            appointment_date_str = input("Enter date (YYYY-MM-DD): ")
            if not validate_date_format(appointment_date_str):
                print("Date format is incorrect. Please use the format YYYY-MM-DD.")
                continue
            appointment_date = datetime.datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            if current_date > appointment_date:
                print("You can only make appointments for future dates.")
                continue

            # Prevent booking for the current day past 16:00
            if current_date == appointment_date and current_time >= datetime.time(16, 0):
                print("You cannot make appointments for today after 16:00.")
                continue

            # Fetch available times for the selected date
            now_available_times = find_reserved_times_by_date(appointment_date_str)
            if not now_available_times:
                print("No available times for this date.")
                continue

            while True:
                appointment_time = input("Enter time (HH:MM): ")
                if not validate_time_format(appointment_time):
                    print("Invalid time format. Please use the format HH:MM.")
                    continue

                appointment_time_obj = datetime.datetime.strptime(appointment_time, '%H:%M').time()

                # Ensure the appointment time is in the future if booking for today
                if current_date == appointment_date and appointment_time_obj <= current_time:
                    print("Appointment time must be in the future.")
                    continue

                # Convert now_available_times to datetime.time objects for proper comparison
                available_time_objects = [datetime.datetime.strptime(t, '%H:%M').time() for t in now_available_times]

                if appointment_time_obj not in available_time_objects:
                    print(f"Invalid appointment time. Available times for {appointment_date_str} are: ", now_available_times)
                    continue

                # Remove the booked time from available times
                now_available_times = [t for t in now_available_times if t != appointment_time]  # Update available times
                break

            break

        reason = input("Enter reason: ")

        appointment = {
            "date": appointment_date_str,
            "time": appointment_time,
            "reason": reason,
            "userId": user_id
        }

        response = requests.post(database_url + "/appointments.json", json=appointment)
        if response.status_code == 200:
            print("Appointment made successfully.")
        else:
            print("Failed to make appointment. Please try again.")
        break


# main function 4: cancel an appointment
def cancel_appointment():
    user_id = input("Enter user ID: ")
    appointments = find_appointments_by_user(user_id)
    if appointments:
        while True:  # the loop continues until the user chooses to exit
            date = input("Enter date (YYYY-MM-DD) of the appointment you want to cancel (or 'q' to quit): ")
            if date.lower() == 'q':
                break  # if the user enters 'q', exit the loop
            time = input("Enter time (HH:MM) of the appointment you want to cancel: ")

            # check if the date and time format is valid
            if not validate_date_format(date) or not validate_time_format(time):
                print("Invalid date or time format. Please try again.")  # 格式错误提示消息
                continue  # restart the loop, allowing the user to re-enter.

            found = False
            for appointment_id, appointment_data in appointments.items():
                if appointment_data["date"] == date and appointment_data["time"] == time:
                    found = True
                    cancel_confirmation = input(
                        f"Do you want to cancel the appointment on {date} at {time}? (yes/no): ")
                    if cancel_confirmation.lower() == 'yes':
                        # delete reservation record
                        hash_value = hash_userId(user_id)
                        database_url = DATABASE_URLS[hash_value]
                        delete_url = f"{database_url}/appointments/{appointment_id}.json"

                        response = requests.delete(delete_url)
                        if response.status_code == 200:
                            print("Appointment canceled successfully.")
                            del appointments[appointment_id]  # remove the canceled reservation record from the local dictionary
                        else:
                            print("Failed to cancel appointment. Please try again.")
                    else:
                        print("Appointment not canceled.")
                    break

            if not found:
                print("No matching appointment found for the provided date and time.")
    else:
        print(f"No appointments found for user {user_id}.")


# main function 5: change an appointment
def change_appointment():
    while True:
        user_id = input("Enter user ID: ")

        # verify if the user exists; if not, ask whether to re-enter the user ID
        while not check_user_exists(user_id):
            reenter = input("User does not exist. Do you want to re-enter user ID? (yes/no): ")
            if reenter.lower() == "yes":
                user_id = input("Enter user ID: ")
            else:
                return

        # find and list the reservations for the specified user
        appointments = find_appointments_by_user(user_id)
        if not appointments:
            print("No appointments found for this user.")
            return

        try:
            # allow the user to choose the reservation date and time to modify
            date_to_change = input("Enter the date you want to change (YYYY-MM-DD): ")
            if not validate_date_format(date_to_change):
                print("Date format is incorrect. Please use the format YYYY-MM-DD.")
                continue

            time_to_change = input("Enter the time you want to change (HH:MM): ")
            if not validate_time_format(time_to_change):
                print("Time format is incorrect. Please use the format HH:MM.")
                continue

            selected_key = None
            for key, appointment in appointments.items():
                if appointment['date'] == date_to_change and appointment['time'] == time_to_change:
                    selected_key = key
                    selected_appointment = appointment
                    break

            if selected_key is None:
                raise ValueError("Appointment not found.")

        except ValueError as e:
            print(str(e))
            continue

        # attempt to convert the input date into a datetime object
        while True:
            try:
                change_date = datetime.datetime.strptime(date_to_change, '%Y-%m-%d')
                change_time = datetime.datetime.strptime(time_to_change, '%H:%M').time()
                break  # If conversion successful, exit the loop
            except ValueError:
                print("Date or time format is incorrect. Please use the format YYYY-MM-DD for date and HH:MM for time.")
                date_to_change = input("Enter date (YYYY-MM-DD): ")
                time_to_change = input("Enter time (HH:MM): ")
                continue

        # convert the date and time into a datetime object
        change_datetime = datetime.datetime.combine(change_date.date(), change_time)

        # attempt to convert the input date into a datetime object for the new date
        while True:
            new_date = input("Enter new date (YYYY-MM-DD): ")
            if validate_date_format(new_date):
                break  # If date format is correct, exit the loop
            else:
                print("Date format is incorrect. Please use the format YYYY-MM-DD.")
                continue

        # attempt to convert the input time into a datetime object for the new time
        while True:
            new_time = input("Enter new time (HH:MM): ")
            if validate_time_format(new_time):
                break  # If time format is correct, exit the loop
            else:
                print("Time format is incorrect. Please use the format HH:MM.")
                continue

        new_reason = input("Enter new reason: ")

        # merge the date and time into one datetime object
        new_datetime = datetime.datetime.combine(datetime.datetime.strptime(new_date, '%Y-%m-%d').date(),
                                                  datetime.datetime.strptime(new_time, '%H:%M').time())

        # check if the new appointment date and time are already reserved
        while True:
            curr_available_times = find_reserved_times_by_date(new_date)
            if new_time not in curr_available_times:
                print("The date and time you're trying to change to are already booked. Please choose another date or time.")
                new_time = input("Enter another new time (HH:MM): ")
                new_reason = input("Enter another new reason: ")
                if not validate_time_format(new_time):
                    print("Time format is incorrect. Please use the format HH:MM.")
                    continue
            else:
                break

        # verify if the new date and time are earlier than the current time
        if new_datetime < datetime.datetime.now():
            print("New appointment date and time cannot be earlier than the current date and time.")
            rebook = input("Do you want to rebook? (yes/no): ")
            if rebook.lower() == "yes":
                continue
            else:
                return

        # Update the appointment information with the new date and time
        hash_value = hash_userId(user_id)
        database_url = DATABASE_URLS[hash_value]
        response = requests.get(database_url + "/appointments.json")
        if response.status_code == 200:
            appointments_data = response.json()
            for key, appointment in appointments_data.items():
                if key == selected_key:
                    appointment["date"] = new_date
                    appointment["time"] = new_time  # Use the updated time here
                    appointment["reason"] = new_reason
                    requests.put(database_url + f"/appointments/{key}.json", json=appointment)
                    print("Appointment changed successfully.")
                    return
        print("Appointment not found.")


# appointments menu
def admin_appointments_menu():
    while True:
        print("1. Find all appointments based on user ID")
        print("2. Find all appointments in a certain date")
        print("3. Make an appointment")
        print("4. Cancel an appointment")
        print("5. Change an appointment")
        print("6. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == "1":
            user_id = input("Enter user ID: ")
            find_appointments_by_user(user_id)
        elif choice == "2":
            find_appointments_by_date()
        elif choice == "3":
            make_appointment()
        elif choice == "4":
            cancel_appointment()
        elif choice == "5":
            change_appointment()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    admin_appointments_menu()
