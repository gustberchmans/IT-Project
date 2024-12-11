import flet as ft
from components.base_layout import BaseLayout
from components.nav_bar import NavBar

def show_learn_page(page: ft.Page, router):
    welcome_text = ft.Text(
        "Welcome to Learning!",
        size=32,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
        font_family="Joan",
    )

    difficulty_section = ft.Container(
        content=ft.Column([
            # Difficulty 1
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(
                            "1", 
                            size=20, 
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        alignment=ft.alignment.center,
                        padding=0,
                        border_radius=50,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        bgcolor=ft.colors.WHITE,
                        width=40,
                        height=40
                    ),
                    ft.Text("Difficulty 1"),
                    ft.TextButton("Start", on_click=lambda e: router.navigate("/difficulty1"))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10,
                padding=15,
                bgcolor=ft.colors.WHITE
            ),
            # Difficulty 2 (new section)
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(
                            "2", 
                            size=20, 
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        alignment=ft.alignment.center,
                        padding=0,
                        border_radius=50,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        bgcolor=ft.colors.WHITE,
                        width=40,
                        height=40
                    ),
                    ft.Text("Difficulty 2"),
                    ft.TextButton("Start", on_click=lambda e: router.navigate("/difficulty2"))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10,
                padding=15,
                bgcolor=ft.colors.WHITE,
                margin=ft.margin.only(top=10)  # Added margin to separate the sections
            ),
        ]),
        padding=25,
        margin=ft.margin.only(top=20, bottom=20),
        border_radius=ft.border_radius.only(top_left=10, top_right=10),
        bgcolor=ft.colors.GREY_200,
        width=page.width,
    )


    nav_bar = NavBar(router=router, active_route="/learn")

    content = ft.Column(
        controls=[ft.Container(height=20),welcome_text, difficulty_section],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    return ft.View(
        route="/learn",
        controls=[content, nav_bar],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0,
    )