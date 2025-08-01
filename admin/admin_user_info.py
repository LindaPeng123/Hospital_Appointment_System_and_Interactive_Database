import json
import requests
import re
from datetime import datetime

DATABASE_URLS = {0: "https://hospital1-850e0-default-rtdb.firebaseio.com",
                 1: "https://hospital-2-f901a-default-rtdb.firebaseio.com",
                 2: "https://hospital-3-502e9-default-rtdb.firebaseio.com"}

def hash_function(userID):
    hash_value = sum(ord(char) for char in userID)
    return hash_value % 3

# check if user id exists
def check_userID(userID):
    db_num = hash_function(userID)
    response = requests.get(f'{DATABASE_URLS[db_num]}/users/{userID}.json')
    data = response.json()
    if data is None:
        return False
    else:
        return True

# check if the entered option numbe is an integer
def check_int(value):
    try:
        int(str(value))
        return True
    except ValueError:
        return False

# check if the entered name follow the format of First_name Last_name
def validate_name(name):
    pattern = r'^[A-Z][a-z]+ [A-Z][a-z]+$'
    return bool(re.match(pattern, name))

# check if the entered date of birth is in the format of MM-DD-YYYY and within the range of 1895-2023
def validate_dob(dob):
    pattern = r'^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])-(18[9][5-9]|19\d{2}|20[0-1][0-9]|202[0-3])$'
    if re.fullmatch(pattern, dob):
        try:
            datetime.strptime(dob, '%m-%d-%Y')
            return True
        except ValueError:
            return False
    else:
        return False

# check if the gender is either male or female
def validate_gender(gender):
    if gender in ['male', 'female']:
        return True
    else:
        return False

# check if it is a valid US phone number
def validate_phoneNo(phone_No):
    pattern = re.compile(r"^\+?1?\s?(\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}$")
    return pattern.match(phone_No) is not None

# check if the entered email address is valid
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# calculate age based on the entered date of birth
def calculate_age(dob):
    dob_date = datetime.strptime(dob, "%m-%d-%Y")
    today = datetime.today()
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    return age

def update_info():
    while True:
        attribute_no = input('1. Name\n'
                             '2. Date of Birth\n'
                             '3. Gender\n'
                             '4. Phone Number\n'
                             '5. Email\n'
                             '6. Allergies\n'
                             '7. Medication\n'
                             '8. Password\n'
                             'Please enter the number of the attribute you want to update: ')
        
        if check_int(attribute_no) and int(attribute_no) in range(1,10):
            attribute_list = ['name', 'date of birth', 'gender', 'phone_number', 'email', 'allergies', 'medication', 'password']
            attribute = attribute_list[int(attribute_no) - 1]
            
            value = input('Please enter the new value of the attribute: ')
            
            if int(attribute_no) == 1:
                while not validate_name(str(value)):
                    value = input('Please enter the valid value for Name (First Name Last Name): ')
                        
            if int(attribute_no) == 2:
                while not validate_dob(str(value)):
                    value = input('Please enter the valid value for Date of Birth (MM-DD-YYY): ')
            
            if int(attribute_no) == 3:
                while not validate_gender(str(value)):
                    value = input('Please enter the valid value for Gender (male / female): ')
            
            if int(attribute_no) == 4:
                while not validate_phoneNo(str(value)):
                    value = input('Please enter the valid Phone Number: ')
            
            if int(attribute_no) == 5:
                while not validate_email(str(value)):
                    value = input('Please enter the valid Email address: ')
            
            return attribute, value
    
        else:
            print('\nPlease enter the valid number of the attribute you want to update!')
    
def search_user_info(userID, update):
    db_num = hash_function(userID)
    response = requests.get(f'{DATABASE_URLS[db_num]}/users.json?orderBy="$key"&equalTo='+f'"{userID}"')
    user_dict = response.json()
    return_keys = ['age', 'date of birth', 'gender', 'phone_number', 'email', 'allergies', 'medication']
    if update:
        print('\nHere is the new information for ' + user_dict[userID]['name'] + ':')
    else:
        print('\nHere is the information for ' + user_dict[userID]['name'] + ':')
    for key in return_keys:
        value = user_dict[userID][key]
        print('  ' + f'{key}: {value}')
    return

def update_user_info(userID, attribute, value):
    db_num = hash_function(userID)
    if attribute == 'date of birth':
        age_value = calculate_age(value)
        new_data = {attribute: value, 'age': age_value}
    else:
        new_data = {attribute: value}
    response = requests.patch(f'{DATABASE_URLS[db_num]}/users/{userID}.json', json = new_data)
    if response.ok:
        print('\nInformation is updated successfully!')
        search_user_info(userID, True)
    return

def delete_user_info(userID):
    db_num = hash_function(userID)

    user_response = requests.delete(f'{DATABASE_URLS[db_num]}/users/{userID}.json')
    if user_response.ok:
        print('User information is deleted successfully!')
    else:
        print('Failed to delete user information!')

    appointments_response = requests.get(f'{DATABASE_URLS[db_num]}/appointments.json')
    if appointments_response.ok:
        appointments = appointments_response.json()
        appointments_deleted = False  # Flag to track if any related appointments were found and deleted
        for appointment_id, appointment_data in appointments.items():
            if appointment_data.get("userId") == userID:

                appointment_response = requests.delete(f'{DATABASE_URLS[db_num]}/appointments/{appointment_id}.json')
                if appointment_response.ok:
                    appointments_deleted = True  # Set the flag to True if any appointment is deleted
                else:
                    print(f'Failed to delete appointment {appointment_id}!')

        # Check if appointments were deleted and print the corresponding message
        if appointments_deleted:
            print('Related appointments are deleted successfully!')
        else:
            print('No related appointments found for deletion.')

    else:
        print('Failed to fetch appointments!')

    return


def create_user_info(userID, DATABASE_URLS):
    name = input("Please enter the Full Name (First Name Last Name): ")
    while not validate_name(str(name)):
        name = input('Please enter the valid value for Full Name (First Name Last Name): ')
        
    password = input("Please enter the Password: ")
    
    dob = input("Please enter the Date of Birth in (MM-DD-YYYY): ")
    while not validate_dob(str(dob)):
        dob = input('Please enter the valid value for Date of Birth (MM-DD-YYY): ')
       
    gender = input("Please enter the Gender (male / female): ")
    while not validate_gender(str(gender)):
        gender = input('Please enter the valid value for Gender (male / female): ')
            
    phone_number = input("Please enter the Phone Number: ")
    while not validate_phoneNo(str(phone_number)):
        phone_number = input('Please enter the valid Phone Number: ')
            
    email = input("Please enter the Email Address: ")
    while not validate_email(str(email)):
        email = input('Please enter the valid Email address: ')
    
    allergies = input("Please enter the allergies (If any): ")
    medication = input("Please enter the medication (If any): ")
    
    database_num = hash_function(userID)
    db_url = DATABASE_URLS[database_num]

    user_data = {"name": name,
                 "password": password,
                 "date of birth": dob,
                 "age": calculate_age(dob),
                 "gender": gender,
                 "phone_number": phone_number,
                 "email": email,
                 "allergies": allergies,
                 "medication": medication}

    response = requests.put(f"{db_url}/users/{userID}.json", json = user_data)
    
    if response.ok:
        print("\nUser information is added successfully!")
    
    return


def admin_user_info_menu():
    key = None
    delete_key = False

    while True:

        if key is None and not delete_key:
            key = input('1. Search user information\n'
                        '2. Update user information\n'
                        '3. Delete user information\n'
                        '4. Create user information\n'
                        '5. Back to Main Menu\n'
                        'Please choose your option: ')

        if delete_key:
            key = '3'

        if not check_int(key) or int(key) not in [1,2,3,4,5]:
            key = None
            print('Please enter valid option number!')
            continue

        if int(key) == 1:

            userID = input('Please enter the User ID: ')

            if check_userID(userID):
                search_user_info(userID, False)

                update_or_not = input('\nDo you want to update this information? (Yes / No)')
                go_back_to_main_menu = False
                while True:
                    if update_or_not == 'No':
                        break
                    elif update_or_not == 'Yes':
                        attribute, value = update_info()
                        update_user_info(userID, attribute, value)
                        key = None
                        go_back_to_main_menu = True
                        break
                    else:
                        update_or_not = input('Please enter Yes or No: ')

                if go_back_to_main_menu:
                    continue

                delete_or_not = input('Do you want to delete this information? (Yes / No)')
                while True:
                    if delete_or_not == 'No':
                        key = None
                        break
                    elif delete_or_not == 'Yes':
                        delete_user_info(userID)
                        key = None
                        break
                    else:
                        delete_or_not = input('Please enter Yes or No: ')

            else:
                print('The User ID is not exist!')

                create_or_not = input('Do you want to create a new User ID? (Yes / No)')
                while create_or_not not in ['Yes', 'No']:
                    create_or_not = input('Please enter Yes or No: ')

                if create_or_not == 'Yes':
                    create_user_info(userID, DATABASE_URLS)
                    search_user_info(userID, False)
                    key = None
                    continue

                else:
                    next_step = input('1. Enter another User ID\n'
                                      '2. Back to the main menu\n'
                                      'Which option do you prefer?')

                while not check_int(next_step) or int(next_step) not in [1,2]:
                    next_step = print('Please enter valid option number: ')

                if int(next_step) == 1:
                    key = '1'
                else:
                    key = None
                    continue


        elif int(key) == 2:

            userID = input('Please enter the User ID: ')

            if check_userID(userID):
                search_user_info(userID, False)

                update_or_not = input('\nDo you want to update this information? (Yes / No)')
                while update_or_not not in ['Yes', 'No']:
                    update_or_not = input('Please enter Yes or No: ')

                if update_or_not == 'Yes':
                    attribute, value = update_info()
                    update_user_info(userID, attribute, value)
                    key = None
                    continue
                else:
                    key = None
                    continue

            else:
                print('The User ID is not exist!')

                create_or_not = input('Do you want to create a new User ID? (Yes / No)')
                while create_or_not not in ['Yes', 'No']:
                    create_or_not = input('Please enter Yes or No: ')

                if create_or_not == 'Yes':
                    create_user_info(userID, DATABASE_URLS)
                    search_user_info(userID, False)
                    key = None
                    continue

                else:
                    next_step = input('1. Enter another User ID\n'
                                      '2. Back to the main menu\n'
                                      'Which option do you prefer?')

                while not check_int(next_step) or int(next_step) not in [1,2]:
                    next_step = print('Please enter valid option number: ')

                if int(next_step) == 1:
                    key = '1'
                else:
                    key = None
                    continue

        elif int(key) == 3:

            userID = input('Please enter the User ID: ')

            if not check_userID(userID):
                while not check_userID(userID):
                    print('The User ID is not exist!')

                    next_step = input('1. Enter another User ID\n'
                                    '2. Back to the main menu\n'
                                    'Which option do you prefer?')
                    while not check_int(next_step) or int(next_step) not in [1,2]:
                        next_step = print('Please enter valid option number: ')

                    if int(next_step) == 1:
                        delete_key = True
                        break
                    else:
                        key = None
                        delete_key = False
                        break
                continue

            else:
                search_user_info(userID, False)
                delete_or_not = input('\nDo you want to delete this information? (Yes / No)')
                while delete_or_not not in ['Yes', 'No']:
                    delete_or_not = input('Please enter Yes or No: ')

                if delete_or_not == 'Yes':
                    delete_user_info(userID)
                    key = None
                    continue
                else:
                    key = None
                    continue

        elif int(key) == 4:

            userID = input('Please enter the User ID: ')
            while check_userID(userID):
                print('The User ID is already exist! Please choose a new one.')
                userID = input('Please enter the User ID: ')

            create_user_info(userID, DATABASE_URLS)
            search_user_info(userID, False)
            key = None
            continue

        elif int(key) == 5:
            break

