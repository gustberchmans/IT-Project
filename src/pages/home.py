import flet as ft
from components.nav_bar import NavBar

def create_difficulty_row(title, router, is_locked=False, progress=None):
    controls = [ft.Text(title)]
    
    if is_locked:
        controls.append(ft.Text("Locked", color=ft.colors.GREY_500))
    else:
        controls.extend([
            ft.ProgressBar(value=progress, width=150),
            ft.TextButton("Continue", on_click=lambda e: router.navigate(f"/difficulty{title[-1]}"))
        ])
    
    return ft.Row(
        controls=controls,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

def show_home_page(page: ft.Page, router):
    page.clean()
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = "#f0f4f8"
    page.padding = 0  # Remove default padding

    welcome_section = ft.Container(
        content=ft.Text(
            "Welcome,",
            size=32,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        ),
        margin=ft.margin.only(top=20, bottom=20),
        padding=ft.padding.symmetric(horizontal=20)
    )

    progress_section = ft.Container(
        content=ft.Column([
            ft.Text("Progress", size=24, weight=ft.FontWeight.BOLD),
            create_difficulty_row("Difficulty 1", router, progress=0.5),
            create_difficulty_row("Difficulty 2", router, is_locked=True),
            create_difficulty_row("Difficulty 3", router, is_locked=True),
            ft.ElevatedButton(
                "Resume",
                on_click=lambda e: router.navigate("/resume"),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                )
            )
        ]),
        padding=20,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.GREY_300)
    )

    streak_text = ft.Container(
        content=ft.Text(
            "Make your streak 15 today!",
            size=16,
            text_align=ft.TextAlign.CENTER,
            color=ft.colors.GREY_800
        ),
        margin=ft.margin.only(bottom=20)
    )

    nav_bar = NavBar(router=router, active_route="/home")
    
    content = ft.Container(
        content=ft.Column(
            controls=[
                welcome_section,
                progress_section,
                streak_text
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        expand=True,
        padding=20
    )

    return ft.View(
        route="/home",
        controls=[content, nav_bar],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )