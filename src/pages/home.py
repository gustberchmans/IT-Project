import flet as ft
from components.nav_bar import NavBar
import json
import os
from datetime import datetime

def load_streak():
    
    json_file = 'src/components/streak.json'
    
    
    print("Loading streak...")
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        last_date = datetime.strptime(data.get('last_date', '2000-01-01'), '%Y-%m-%d').date()
        current_date = datetime.now().date()
        current_streak = data.get('streak', 0)
        total_days = data.get('total_days', 0)
        
        #debug print
        print(f"Last date: {last_date}")
        print(f"Current date: {current_date}")
        print(f"Current streak: {current_streak}")
        
        # Calculate if streak should be updated
        days_difference = (current_date - last_date).days
        print(f"Days difference: {days_difference}")
        
        if days_difference > 1:  # Streak broken
            print("Streak broken - resetting to 0")
            current_streak = 0
        elif days_difference == 1:  # New day, increment streak
            print("New day - incrementing streak")
            current_streak += 1
            total_days += 1
        else:
            print("Same day - keeping current streak")
        
        # Save updated streak
        with open(json_file, 'w') as f:
            json.dump({
                "streak": current_streak,
                "last_date": current_date.strftime('%Y-%m-%d'),
                "total_days": total_days
            }, f, indent=4)
            
        print(f"Final streak value: {current_streak}")
        return current_streak
        
    except Exception as e:
        print(f"Error handling streak: {e}")
        return 0

def load_progress():
    json_file = 'src/components/progress.json'
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading progress: {e}")
        return {"difficulty1": 0, "difficulty2": 0, "difficulty3": 0}

def save_progress(difficulty_number, progress_value):
    json_file = 'src/components/progress.json'
    try:
        current_progress = load_progress()
        current_progress[f"difficulty{difficulty_number}"] = progress_value
        
        with open(json_file, 'w') as f:
            json.dump(current_progress, f, indent=4)
    except Exception as e:
        print(f"Error saving progress: {e}")

def create_difficulty_row(title, router, is_locked=False, progress=None):
    difficulty_number = title[-1]  # Get the difficulty number from title
    progress_data = load_progress()
    current_progress = progress_data[f"difficulty{difficulty_number}"]
    
    controls = [
        ft.Container(
            content=ft.Text(title),
            width=100
        )
    ]
    
    if is_locked:
        controls.append(
            ft.Container(
                content=ft.Text("Locked", color=ft.colors.GREY_500),
                alignment=ft.alignment.center_right
            )
        )
    else:
        controls.extend([
            ft.ProgressBar(
                value=current_progress,
                width=100,
                bgcolor=ft.colors.GREY_300,
                color=ft.colors.BLUE,
            ),
            ft.Container(
                content=ft.TextButton("Continue", 
                    on_click=lambda e: router.navigate(f"/difficulty{difficulty_number}")
                ),
                width=100,
                alignment=ft.alignment.center_right
            )
        ])
    
    return ft.Row(
        controls=controls,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        width=400
    )

def load_days_progress():
    json_file = 'src/components/streak.json'
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            return data.get('total_days', 0)
    except:
        return 0

def show_home_page(page: ft.Page, router):
    page.clean()
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = "#f0f4f8"
    page.padding = 0  

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

    # Update streak_text to use the dynamic streak
    current_streak = load_streak()
    streak_message = (
        "Start your streak today!" if current_streak == 0 
        else f"Make your streak {current_streak + 1} today!"
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
    total_days = load_days_progress()
    
    monthly_progress = min(total_days / 30, 1.0)
    days_left_monthly = max(30 - total_days, 0)
    
    monthly_progress_row = ft.Row(
        controls=[
            ft.Text("30 Days Goal:", size=14),
            ft.ProgressBar(value=monthly_progress, width=100),
            ft.Text(f"{days_left_monthly} days left", size=14)
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        width=400
    )

    yearly_progress = min(total_days / 365, 1.0)
    days_left_yearly = max(365 - total_days, 0)
    
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