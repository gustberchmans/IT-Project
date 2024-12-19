import flet as ft
from services.auth import register_user
from utils.helpers import show_error_snackbar, show_success_snackbar

def show_register_page(page: ft.Page, router):
    page.clean()
    page.window.width = 400
    page.window.height = 800
    page.bgcolor = "#f0f4f8"

    firstname_input = ft.TextField(
        label="First Name",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        prefix_icon=ft.icons.PERSON,
        cursor_color=ft.colors.BLUE,
        focused_border_color=ft.colors.BLUE,
        text_size=16
    )

    lastname_input = ft.TextField(
        label="Last Name",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        prefix_icon=ft.icons.PERSON,
        cursor_color=ft.colors.BLUE,
        focused_border_color=ft.colors.BLUE,
        text_size=16
    )

    email_input = ft.TextField(
        label="Email",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        prefix_icon=ft.icons.EMAIL,
        cursor_color=ft.colors.BLUE,
        focused_border_color=ft.colors.BLUE,
        text_size=16
    )

    password_input = ft.TextField(
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

    def handle_register(e):
        if not all([firstname_input.value, lastname_input.value, email_input.value, password_input.value]):
            show_error_snackbar(page, "Please fill in all fields")
            return

        result = register_user(
            email_input.value,
            password_input.value,
            firstname_input.value,
            lastname_input.value
        )

        if result['success']:
            show_success_snackbar(page, "Registration successful!")
            router.navigate("/login")
        else:
            show_error_snackbar(page, result['error'])
            page.update()

    register_button = ft.ElevatedButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.APP_REGISTRATION),
                ft.Text("Register", size=16, weight=ft.FontWeight.BOLD)
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
        on_click=handle_register
    )

    login_link = ft.TextButton(
        "Already have an account? Login",
        icon=ft.icons.LOGIN,
        on_click=lambda _: router.navigate("/login")
    )

    content = ft.Column(
        controls=[
            ft.Container(
                content=ft.Icon(
                    ft.icons.SIGN_LANGUAGE_ROUNDED,
                    size=80,
                    color=ft.colors.BLUE
                ),
                margin=ft.margin.only(top=40, bottom=20)
            ),
            ft.Text(
                "Create Account",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.BLUE_900
            ),
            ft.Text(
                "Sign up to get started",
                size=16,
                color=ft.colors.GREY_700,
                weight=ft.FontWeight.W_500
            ),
            ft.Container(height=20),
            firstname_input,
            lastname_input,
            email_input,
            password_input,
            ft.Container(height=20),
            register_button,
            login_link
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    return ft.View(
        route="/register",
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )