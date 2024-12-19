import flet as ft
from components.nav_bar import NavBar
from services.firebase import update_streak, get_streak, load_progress, get_current_user

def create_difficulty_row(difficulty_name, router, progress=0, is_locked=False):
    return ft.Row(
        controls=[
            ft.Text(difficulty_name, size=16),
            ft.ProgressBar(value=progress, width=100),
            ft.IconButton(
                icon=ft.Icons.LOCK if is_locked else ft.Icons.ARROW_FORWARD,
                on_click=lambda e: router.navigate(f"/{difficulty_name.lower().replace(' ', '')}"),
                disabled=is_locked
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        width=400
    )

def get_next_unfinished_lesson(progress_data):
    """
    Returns the path to the next unfinished lesson based on the user's progress.
    """
    for difficulty in ['difficulty1', 'difficulty2', 'difficulty3']:
        for level in ['d1l1', 'd1l2', 'd1l3'] if difficulty == 'difficulty1' else ['d2l1', 'd2l2', 'd2l3'] if difficulty == 'difficulty2' else ['d3l1', 'd3l2', 'd3l3']:
            if progress_data[difficulty][level] == 0:  # if the level is not completed
                # return the path of the next unfinished level
                return f"/{level}"
    return None  # If all lessons are completed

def show_home_page(page: ft.Page, router):
    page.clean()
    page.window.width = 400
    page.window.height = 800
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

    # Check if Difficulty 1 and Difficulty 2 are completed
    is_difficulty1_complete = (
        progress_data["difficulty1"]["d1l1"] == 1 and
        progress_data["difficulty1"]["d1l2"] == 1 and
        progress_data["difficulty1"]["d1l3"] == 1
    )
    is_difficulty2_complete = (
        progress_data["difficulty2"]["d2l1"] == 1 and
        progress_data["difficulty2"]["d2l2"] == 1 and
        progress_data["difficulty2"]["d2l3"] == 1
    )

    # Get the next unfinished lesson
    next_lesson = get_next_unfinished_lesson(progress_data)
    
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
            create_difficulty_row(
                "Difficulty 1", 
                router, 
                progress=(
                    progress_data["difficulty1"]["d1l1"] +
                    progress_data["difficulty1"]["d1l2"] +
                    progress_data["difficulty1"]["d1l3"]
                ) / 3
            ),
            create_difficulty_row(
                "Difficulty 2", 
                router, 
                progress=(
                    progress_data["difficulty2"]["d2l1"] +
                    progress_data["difficulty2"]["d2l2"] +
                    progress_data["difficulty2"]["d2l3"]
                ) / 3,
                is_locked=not is_difficulty1_complete  # Unlock Difficulty 2 if Difficulty 1 is complete
            ),
            create_difficulty_row(
                "Difficulty 3", 
                router, 
                progress=(
                    progress_data["difficulty3"]["d3l1"] +
                    progress_data["difficulty3"]["d3l2"] +
                    progress_data["difficulty3"]["d3l3"]
                ) / 3,
                is_locked=not is_difficulty2_complete  # Unlock Difficulty 3 if Difficulty 2 is complete
            ),
            ft.ElevatedButton(
                "Resume",
                on_click=lambda e: router.navigate(next_lesson if next_lesson else "/home"),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                )
            )
        ]), 
        padding=20,
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.GREY_300)
    )

    streak_text = ft.Container(
        content=ft.Text(
            streak_message,
            size=16,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.GREY_800
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
