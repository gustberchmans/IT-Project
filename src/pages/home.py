import flet as ft
from components.nav_bar import NavBar
from services.firebase import update_streak, get_streak, load_progress, get_current_user

def create_difficulty_row(difficulty_name, router, progress=0, is_locked=False):
    return ft.Row(
        controls=[
            ft.Text(difficulty_name, size=16),
            ft.ProgressBar(value=progress, width=100),
            ft.IconButton(
                icon=ft.icons.LOCK if is_locked else ft.icons.ARROW_FORWARD,
                on_click=lambda e: router.navigate(f"/{difficulty_name.lower().replace(' ', '')}"),
                disabled=is_locked
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        width=400
    )

def show_home_page(page: ft.Page, router):
    page.clean()
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = "#f0f4f8"
    page.padding = 0  

    # Define user_id
    
    user_id = get_current_user()

    # Haal de streak en totaal aantal dagen op
    current_streak, total_days = update_streak(user_id)
    streak_message = (
        "Start your streak today!" if current_streak == 0 
        else f"Make your streak {current_streak + 1} today!"
    )
    
    # Haal de voortgang op
    progress_data = load_progress(user_id)

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
            create_difficulty_row("Difficulty 1", router, progress=progress_data["difficulty1"]),
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
            streak_message,
            size=16,
            text_align=ft.TextAlign.CENTER,
            color=ft.colors.GREY_800
        ),
        margin=ft.margin.only(bottom=20)
    )

    # Add these new progress bars after streak_text
    monthly_progress = min(current_streak / 30, 1.0)
    days_left_monthly = max(30 - current_streak, 0)
    
    monthly_progress_row = ft.Row(
        controls=[
            ft.Text("30 Days Goal:", size=14),
            ft.ProgressBar(value=monthly_progress, width=100),
            ft.Text(f"{days_left_monthly} days left", size=14)
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        width=400
    )

    yearly_progress = min(current_streak / 365, 1.0)
    days_left_yearly = max(365 - current_streak, 0)
    
    yearly_progress_row = ft.Row(
        controls=[
            ft.Text("365 Days Goal:", size=14),
            ft.ProgressBar(value=yearly_progress, width=100),
            ft.Text(f"{days_left_yearly} days left", size=14)
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        width=400
    )

    nav_bar = NavBar(router=router, active_route="/home")
    
    content = ft.Container(
        content=ft.Column(
            controls=[
                welcome_section,
                progress_section,
                streak_text,
                monthly_progress_row,
                yearly_progress_row,
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