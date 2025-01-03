import flet as ft
from services.auth import login_user, login_test_user
from utils.helpers import show_error_snackbar, show_success_snackbar
from services.firebase import set_current_user

def show_login_page(page: ft.Page, router):
    page.window.width = 400
    page.window.height = 800

    email_field = ft.TextField(
        label="Email",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        prefix_icon=ft.Icons.EMAIL,
        cursor_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.BLUE,
        text_size=16
    )

    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border=ft.InputBorder.UNDERLINE,
        width=300,
        prefix_icon=ft.Icons.LOCK,
        cursor_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.BLUE,
        text_size=16
    )

    def handle_login(e):
        if not email_field.value or not password_field.value:
            show_error_snackbar(page, "Please fill in all fields")
            return

        result = login_user(email_field.value, password_field.value)
        if result['success']:
            print(result['user_id'])
            set_current_user(result['user_id'])
            
            show_success_snackbar(page, "Login successful!")
            router.navigate("/home")
        else:
            show_error_snackbar(page, result['error'])
            page.update()

    login_button = ft.ElevatedButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LOGIN),
                ft.Text("Login", size=16, weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=300,
        height=45,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=handle_login
    )

    register_button = ft.TextButton(
        "Don't have an account? Register",
        icon=ft.Icons.PERSON_ADD,
        on_click=lambda _: router.navigate("/register")
    )
    
    content = ft.Column(
        controls=[
            ft.Container(
                content=ft.Icon(
                    ft.Icons.SIGN_LANGUAGE_ROUNDED,
                    size=80,
                    color=ft.Colors.BLUE
                ),
            ),
            ft.Text(
                "Welcome Back!",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_900
            ),
            ft.Text(
                "Sign in to continue",
                size=16,
                color=ft.Colors.GREY_700,
                weight=ft.FontWeight.W_500
            ),
          
            email_field,
            password_field,
            ft.Container(height=20),
            login_button,
            register_button
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    return ft.View(
        route="/login",
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )