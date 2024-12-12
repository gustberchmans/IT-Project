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
        else:
            print("Same day - keeping current streak")
        
        # Save updated streak
        with open(json_file, 'w') as f:
            json.dump({
                "streak": current_streak,
                "last_date": current_date.strftime('%Y-%m-%d')
            }, f, indent=4)
            
        print(f"Final streak value: {current_streak}")
        return current_streak
        
    except Exception as e:
        print(f"Error handling streak: {e}")
        return 0

def create_difficulty_row(title, router, is_locked=False, progress=None):
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
            ft.ProgressBar(value=progress, width=100),
            ft.Container(
                content=ft.TextButton("Continue", 
                    on_click=lambda e: router.navigate(f"/difficulty{title[-1]}")
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