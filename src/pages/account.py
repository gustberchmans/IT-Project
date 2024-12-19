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
                'password': hashed_password.decode('utf-8')
            })

            # Update the user data in memory
            user_data.update({
                'firstname': new_firstname,
                'lastname': new_lastname,
                'email': new_email,
                'password': hashed_password.decode('utf-8')
            })
            print("User updated successfully!")
            print("--------------------------")

            show_success_snackbar(page, "Profile updated successfully!")
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            show_error_snackbar(page, f"Error updating profile: {str(e)}")

    # Add back button in header
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_BACK,
        on_click=handle_back,
        icon_color=ft.colors.BLACK
    )

    # Update the profile section styling
    name_field = ft.TextField(
        value=f"{user_data['firstname']} {user_data['lastname']}", 
        prefix_icon=ft.icons.PERSON,
        label="Full Name",
        border=ft.InputBorder.UNDERLINE,
        height=50,
    )

    email_field = ft.TextField(
        value=user_data['email'],
        prefix_icon=ft.icons.EMAIL,
        label="Email",
        border=ft.InputBorder.UNDERLINE,
        height=50,
    )

    password_field = ft.TextField(
        value="",
        prefix_icon=ft.icons.LOCK,
        password=True,
        can_reveal_password=True,
        label="New Password",
        border=ft.InputBorder.UNDERLINE,
        height=50,
    )

    profile_section = ft.Container(
        content=ft.Column([
            # Custom header with back button
            ft.Container(
                content=ft.Row([
                    back_button,
                    ft.Text("Profile", size=24, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.only(bottom=20),
            ),
            # Profile picture with network image
            ft.Container(
                content=ft.CircleAvatar(
                    foreground_image_url="https://picsum.photos/200",
                    radius=75,
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(bottom=20),
            ),
            # Form fields in a card
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        name_field,
                        email_field,
                        password_field,
                    ], spacing=10),
                    padding=20,
                ),
                elevation=0,
            ),

            # Centered Save Profile button
            ft.Container(
                content=ft.ElevatedButton(
                    "Save profile",
                    on_click=handle_save_profile,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE,
                        shape=ft.RoundedRectangleBorder(radius=25),
                    ),
                    width=300,  # Made button wider
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=20),
            ),
        ]),
        padding=20,
    )

    # Create a stack to overlay the logout button
    page_content = ft.Stack([
        profile_section,
        # Logout button positioned in top-right corner
        ft.Container(
            content=ft.IconButton(
                icon=ft.icons.LOGOUT,
                icon_color=ft.colors.RED_500,
                on_click=handle_logout,
                tooltip="Logout",  # Added tooltip for better UX
            ),
            alignment=ft.alignment.top_right,
            padding=ft.padding.only(top=20, right=20),
        ),
    ])

    nav_bar = NavBar(router=router, active_route="/account")

    return ft.View(
        route="/account",
        controls=[page_content, nav_bar],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0
    )