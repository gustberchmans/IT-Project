import flet as ft
from components.base_layout import BaseLayout
from components.nav_bar import NavBar
from services.firebase import load_progress, get_current_user  

def is_difficulty_complete(progress_data, difficulty_key):
   
    return all(progress_data[difficulty_key][level] == 1 for level in progress_data[difficulty_key])


def create_difficulty_row(difficulty_name, router, is_locked=False):
    
    return ft.Container(
        content=ft.Row([
            ft.Text(
                difficulty_name,  
                size=16,  
                weight=ft.FontWeight.NORMAL,
                text_align=ft.TextAlign.CENTER
            ),
            ft.TextButton(
                "Start",
                on_click=lambda e, d=difficulty_name: router.navigate(f"/{d.replace(' ', '').lower()}"),
                disabled=is_locked  
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=10,  
        bgcolor=ft.colors.TRANSPARENT,  
        margin=ft.margin.only(top=10) if difficulty_name != "Difficulty 1" else ft.margin.only(top=0)  # Margin alleen als het niet de eerste is
    )

def show_learn_page(page: ft.Page, router):
    
    user_id = get_current_user()
    progress_data = load_progress(user_id)

    
    is_difficulty1_complete = is_difficulty_complete(progress_data, "difficulty1")
    is_difficulty2_complete = is_difficulty_complete(progress_data, "difficulty2")
    

    difficulty_rows = [
        create_difficulty_row(
            "Difficulty 1", 
            router, 
            is_locked=False  
        ),
        create_difficulty_row(
            "Difficulty 2", 
            router, 
            is_locked=not is_difficulty1_complete 
        ),
        create_difficulty_row(
            "Difficulty 3", 
            router, 
            is_locked=not is_difficulty2_complete  
        ),
    ]
    
    
    difficulty_section = ft.Container(
        content=ft.Column(difficulty_rows),
        padding=25,
        margin=ft.margin.only(top=20, bottom=20),
        border_radius=ft.border_radius.only(top_left=10, top_right=10),
        bgcolor=ft.colors.GREY_200,
        width=page.width,
    )

    
    nav_bar = NavBar(router=router, active_route="/learn")

    
    content = ft.Column(
        controls=[ft.Container(height=20), ft.Text("Welcome to Learning!", size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER), difficulty_section],
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
