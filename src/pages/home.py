import flet as ft
from components.nav_bar import NavBar

def show_home_page(page: ft.Page, router):
    page.clean()
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = "#f0f4f8"

    welcome_text = ft.Text(
        "Welcome,",
        size=32,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )

    progress_section = ft.Container(
        content=ft.Column([
            ft.Text("Progress", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Text("Difficulty 1"),
                ft.ProgressBar(value=0.5, width=150),
                ft.TextButton("Continue", on_click=lambda e: router.navigate("/difficulty1"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.Text("Difficulty 2"),
                ft.Text("Locked", color=ft.colors.GREY_500)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.Text("Difficulty 3"),
                ft.Text("Locked", color=ft.colors.GREY_500)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ElevatedButton("Resume", on_click=lambda e: router.navigate("/resume"))
        ]),
        padding=20,
        margin=ft.margin.only(top=20, bottom=20),
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.GREY_300)
    )

    streak_text = ft.Text(
        "Make your streak 15 today!",
        size=16,
        text_align=ft.TextAlign.CENTER
    )

    nav_bar = NavBar(router=router, active_route="/home")

    content = ft.Column(
        controls=[welcome_text, progress_section, streak_text],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    return ft.View(
        route="/home",
        controls=[content, nav_bar],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )