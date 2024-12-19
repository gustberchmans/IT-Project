import flet as ft
from components.base_layout import BaseLayout
from components.nav_bar import NavBar

def show_d1learn_page(page: ft.Page, router):
    lessons = ["Lesson 1", "Lesson 2", "Lesson 3"]  # Hier kun je jouw lessen definiëren

    lesson_buttons = ft.Column([
        ft.Container(
                content=ft.Row([
                    ft.Text(lesson),
                    ft.TextButton(
                        "Open", 
                        on_click=lambda e, l=lesson: router.navigate(f"/d1l{lessons.index(l) + 1}")
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                bgcolor=ft.Colors.WHITE,
                margin=ft.margin.only(top=10)
            ) for lesson in lessons
        ])


    back_button = ft.TextButton("Back", on_click=lambda e: router.navigate("/learn"))

    content = ft.Column(
        controls=[
            ft.Text("Difficulty 1 Lessons", size=24, weight=ft.FontWeight.BOLD),
            lesson_buttons,
            back_button
        ],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    return ft.View(
        route="/difficulty1",
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=20,
    )