
from admin_user_info import admin_user_info_menu
from admin_appointments import admin_appointments_menu
import sys

def main_menu():
    while True:
        print("1. Admin User Information")
        print("2. Admin Appointment")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            admin_user_info_menu()  
        elif choice == "2":
            admin_appointments_menu()  
        elif choice == "3":
            print("Exiting the program...")
            sys.exit()  
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()