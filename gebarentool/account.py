import flet as ft

def show_page3(page, show_main_page, show_page1):
    page.clean()

    # Navigation bar
    nav_bar = ft.Row(
        controls=[
            ft.ElevatedButton("Learn", on_click=lambda e: show_page1(page, show_main_page, show_page3)),
            ft.ElevatedButton("Translate", on_click=lambda e: show_main_page()),
            ft.ElevatedButton("Account", on_click=lambda e: show_page3(page, show_main_page, show_page1)),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    page.add(
        ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(" Account", size=24),
                    padding=ft.padding.only(top=30),
                    border_radius=ft.border_radius.all(8),
                ),
                ft.Container(
                    content=ft.Divider(
                        thickness=2,  # Line thickness
                        color="white",  # Line color
                    ),
                    padding=ft.padding.only(bottom=750),  # Add padding below the divider
                ),
                nav_bar  # Navigation bar at the bottom
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True  # Ensures the column takes up all available vertical space
        )
    )
