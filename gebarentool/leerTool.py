import flet as ft

def show_page1(page, show_main_page, show_page3):
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

    # Page layout with horizontal line and navigation bar
    page.add(
        ft.Column(
            controls=[
                # Display "SMOG" with some padding
                ft.Container(
                    content=ft.Text(" SMOG \/", size=24),
                    padding=ft.padding.only(top=30),
                ),
                # Add a horizontal line (Divider) to span the width of the page
                ft.Container(
                    content=ft.Divider(
                        thickness=2,  # Line thickness
                        color="white",  # Line color
                    ),
                    padding=ft.padding.only(bottom=750),  # Add padding below the divider
                ),
                
                # Navigation bar at the bottom
                nav_bar
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Align text and line at the top
            expand=True  # Ensures the column takes up available vertical space
        )
    )
