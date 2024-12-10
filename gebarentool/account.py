import flet as ft
from firebase_config import get_current_user, get_user_data, logout
from utils import show_success_snackbar, show_error_snackbar
from register import show_register_page
from login import show_login_page

def account(page, show_main_page, leerTool, account):
    page.clean()
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = "#f0f4f8"
    
    # Get user data from Firebase
    user_id = get_current_user()
    user_data = get_user_data(user_id)
    
    def handle_logout(e):
        logout()
        show_success_snackbar(page, "Logged out successfully!")
        show_login_page(page, show_main_page, lambda p, m, l: show_register_page(p, m, l))

    # Profile section with user info
    profile_section = ft.Container(
        content=ft.Column([
            # Profile Picture/Avatar
            ft.Container(
                content=ft.CircleAvatar(
                    content=ft.Text(user_data['firstname'][0].upper()),
                    radius=50,
                    bgcolor=ft.colors.BLUE_200,
                ),
                alignment=ft.alignment.center,
            ),
            # User Name and Email
            ft.Text(
                f"{user_data['firstname']} {user_data['lastname']}", 
                size=24, 
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                user_data['email'], 
                size=16, 
                color=ft.colors.GREY_700,
                text_align=ft.TextAlign.CENTER
            ),
            # Logout Button
            ft.Container(
                content=ft.ElevatedButton(
                    "Logout",
                    icon=ft.icons.LOGOUT,
                    on_click=handle_logout,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor="red",
                    ),
                ),
                margin=ft.margin.only(top=20),
            ),
        ]),
        padding=20,
        alignment=ft.alignment.center,
    )

    # Navigation Bar
    nav_bar = ft.Row(
        controls=[
            ft.ElevatedButton("Learn", on_click=lambda e: leerTool(page, show_main_page, account, leerTool)),
            ft.ElevatedButton("Translate", on_click=lambda e: show_main_page()),
            ft.ElevatedButton("Account", on_click=lambda e: None),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    # Add everything to the page
    page.add(
        ft.Column(
            controls=[
                profile_section,
                nav_bar
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True
        )
    ) 