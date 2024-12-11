import flet as ft
from services.firebase import get_current_user, get_user_data, logout
from utils.helpers import show_success_snackbar, show_error_snackbar
from components.nav_bar import NavBar

def show_account_page(page: ft.Page, router):
    
    user_id = get_current_user()
    user_data = get_user_data(user_id)

    if user_data is None:
        show_error_snackbar(page, "User data not found.")
        router.navigate("/login")
        return

    def handle_logout(e):
        logout()
        show_success_snackbar(page, "Logged out successfully!")
        router.navigate("/login")

    profile_section = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.CircleAvatar(
                    content=ft.Text(user_data['firstname'][0].upper()),
                    radius=50,
                    bgcolor=ft.colors.BLUE_200,
                ),
                alignment=ft.alignment.center,
            ),
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

    nav_bar = NavBar(router=router, active_route="/account")

    return ft.View(
        route="/account",
        controls=[profile_section, nav_bar],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )