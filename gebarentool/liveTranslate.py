import flet as ft

def show_page2(page, show_main_page, show_page2, show_page3):
    page.clean()

    # Navigation bar
    nav_bar = ft.Row(
        controls=[
            ft.ElevatedButton("Learn", on_click=lambda e: show_page1(page, show_main_page, show_page2, show_page3)),
            ft.ElevatedButton("Translate", on_click=lambda e: show_page2(page, show_main_page, show_page1, show_page3)),
            ft.ElevatedButton("Account", on_click=lambda e: show_page3(page, show_main_page, show_page1, show_page2)),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    # Page layout with Back button and Navigation bar
    page.add(
        ft.Column(
            controls=[
                ft.Text("Page 1: Content from File 1", size=24),
                nav_bar  # Navigation bar at the bottom
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Space between the content
            expand=True  # Ensures column takes up available vertical space
        )
    )
