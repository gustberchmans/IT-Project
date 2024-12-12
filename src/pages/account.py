import flet as ft
from services.firebase import get_current_user, get_user_data, logout, db
from utils.helpers import show_success_snackbar, show_error_snackbar
from components.nav_bar import NavBar
from components.header import HeaderBar
from services.auth import hash_password

def show_account_page(page: ft.Page, router):
    user_id = get_current_user()
    user_data = get_user_data(user_id)

    if user_data is None:
        show_error_snackbar(page, "User data not found.")
        router.navigate("/home")
        return

    def handle_logout(e):
        logout()
        show_success_snackbar(page, "Logged out successfully!")
        router.navigate("/login")

    def handle_back(e):
        router.navigate_back()

    def handle_save_profile(e):
        try:
            # Get the updated values from text fields
            new_name = name_field.value.split()
            if len(new_name) != 2:
                show_error_snackbar(page, "Please enter both first and last name.")
                return
                
            new_firstname, new_lastname = new_name
            new_email = email_field.value
            new_password = password_field.value.replace('•', '') if not password_field.password else password_field.value
            hashed_password = hash_password(new_password)

            # Update the database
            db.collection('Users').document(user_id).update({
                'firstname': new_firstname,
                'lastname': new_lastname,
                'email': new_email,
                'password': hashed_password
            })

            # Update the user data in memory
            user_data.update({
                'firstname': new_firstname,
                'lastname': new_lastname,
                'email': new_email,
                'password': hashed_password
            })

            show_success_snackbar(page, "Profile updated successfully!")
        except Exception as e:
            show_error_snackbar(page, f"Error updating profile: {str(e)}")

    name_field = ft.TextField(
        value=f"{user_data['firstname']} {user_data['lastname']}", 
        prefix_icon=ft.icons.PERSON,
        label="Full Name"
    )

    email_field = ft.TextField(
        value=user_data['email'],
        prefix_icon=ft.icons.EMAIL,
        label="Email"
    )

    password_field = ft.TextField(
        value="",
        prefix_icon=ft.icons.LOCK,
        password=True,
        can_reveal_password=True,
        label="New Password"
    )

    profile_section = ft.Container(
        content=ft.Column([
            HeaderBar(router),
            ft.Text(f"{user_data['firstname']} {user_data['lastname']}", size=24, weight=ft.FontWeight.BOLD),
            ft.Icon(ft.icons.PERSON_PIN, size=80),
            name_field,
            email_field,
            password_field,
            ft.ElevatedButton(
                "Save profile",
                on_click=handle_save_profile,
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.BLUE,
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
            ),
            ft.ElevatedButton(
                "Logout",
                icon=ft.icons.LOGOUT,
                on_click=handle_logout,
                bgcolor="red",
                color=ft.colors.WHITE
            ),
        ]),
        padding=20,
        alignment=ft.alignment.center,
    )

    nav_bar = NavBar(router=router, active_route="/account")

    return ft.View(
        route="/account",
        controls=[profile_section, nav_bar],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0
    )