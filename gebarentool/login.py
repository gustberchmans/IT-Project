import flet as ft
from firebase_config import verify_user, set_current_user
from auth import login_user
from utils import show_error_snackbar, show_success_snackbar

def show_login_page(page, on_success, on_register):
    page.clean()
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = "#f0f4f8"  # Light blue-gray background
    
    email_field = ft.TextField(
        label="Email",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        prefix_icon=ft.icons.EMAIL,
        cursor_color=ft.colors.BLUE,
        focused_border_color=ft.colors.BLUE,
        text_size=16
    )
    
    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border=ft.InputBorder.UNDERLINE,
        width=300,
        prefix_icon=ft.icons.LOCK,
        cursor_color=ft.colors.BLUE,
        focused_border_color=ft.colors.BLUE,
        text_size=16
    )

    def handle_login(e):
        if not email_field.value or not password_field.value:
            show_error_snackbar(page, "Please fill in all fields")
            return

        result = login_user(email_field.value, password_field.value)
        if result['success']:
            set_current_user(result['user_id'])
            show_success_snackbar(page, "Login successful!")
            on_success()
        else:
            show_error_snackbar(page, result['error'])
            page.update()

    login_button = ft.ElevatedButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.LOGIN),
                ft.Text("Login", size=16, weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=300,
        height=45,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=handle_login
    )

    register_button = ft.TextButton(
        "Don't have an account? Register",
        icon=ft.icons.PERSON_ADD,
        on_click=lambda _: on_register(page, on_success, show_login_page)
    )

    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            ft.icons.SIGN_LANGUAGE_ROUNDED,
                            size=80,
                            color=ft.colors.BLUE
                        ),
                        margin=ft.margin.only(top=60, bottom=20)
                    ),
                    ft.Text(
                        "Welcome Back!",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_900
                    ),
                    ft.Text(
                        "Sign in to continue",
                        size=16,
                        color=ft.colors.GREY_700,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Container(height=20),
                    email_field,
                    password_field,
                    ft.Container(height=20),
                    login_button,
                    register_button
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=20,
            expand=True
        )
    ) 