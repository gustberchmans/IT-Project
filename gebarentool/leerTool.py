import flet as ft
from dif1 import show_dif1_page

def leerTool(page, show_main_page, leerTool, account):
    page.clean()

    # Navigation bar`   `
    nav_bar = ft.Row(
        controls=[
            ft.ElevatedButton("Learn", on_click=lambda e: None),
            ft.ElevatedButton("Translate", on_click=lambda e: show_main_page()),
            ft.ElevatedButton("Account", on_click=lambda e: account(page, show_main_page, account, leerTool)),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    # Page layout with SMOG text and divider in a row, followed by welcome message and buttons
    page.add(
        ft.Column(
            controls=[
                # Row to place SMOG text and Divider next to each other
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Text("SMOG", size=24),
                            alignment=ft.alignment.center_left,  # Align SMOG text to the left
                            padding=ft.padding.only(top=30, left=10)  # Add space between the text and divider
                        ),
                        ft.Container(
                            content=ft.Divider(  # Divider inside the content
                                thickness=2,  # Line thickness
                                color="black",  # Line color
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,  # Align the row to the start of the page
                    spacing=10  # Space between text and divider
                ),

                # Container for welcome message and buttons
                ft.Container(
                    content=ft.Column(
                        controls=[
                            # Welcome message
                            ft.Container(
                                content=ft.Text("Welcome back!", size=40, weight="bold", color="blue"),
                                padding=ft.padding.only(bottom=50)  # Add space below the welcome message
                            ),
                            # Stacked buttons
                            ft.Container(
                              ft.Column(
                                  controls=[
                                      ft.ElevatedButton("Difficulty 1", on_click=lambda e: show_dif1_page(page, show_main_page, show_page3)),
                                      ft.ElevatedButton("Difficulty 2", on_click=lambda e: print("Option 2 clicked")),
                                      ft.ElevatedButton("Difficulty 3", on_click=lambda e: print("Option 3 clicked")),
                                  ],
                                  alignment=ft.MainAxisAlignment.CENTER,
                                  spacing=10,  # Space between buttons
                              ),
                              padding=ft.padding.only(left=90)
                            ),
                            ft.Container(
                                content=ft.Text("Extend your streak to 15!", size=20, weight="bold", color="blue"),
                                padding=ft.padding.only(bottom=50, top=50, left=30)  # Add space below the welcome message
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,  # Center the entire column
                        spacing=20,  # Space between the welcome message and the buttons
                    ),
                    alignment=ft.alignment.center,  # Center the container horizontally
                    padding=ft.padding.only(top=20),  # Padding above the container
                ),
                
                # Navigation bar at the bottom
                nav_bar
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Align main content and nav bar
            expand=True  # Ensures the column takes up available vertical space
        )
    )
