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

    # Page layout with merged SMOG text and horizontal line
    page.add(
        ft.Column(
            controls=[
                # Row to place SMOG text and Divider next to each other
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(" SMOG", size=24),
                            alignment=ft.alignment.center_left,  # Align SMOG text to the left
                            padding=ft.padding.only(top=30)  # Add space between the text and divider
                        ),
                        ft.Container(
                          ft.Divider(
                              thickness=2,  # Line thickness
                              color="black",  # Line color
                          ),
                          padding=ft.padding.only(top=10)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,  # Align the row to the start of the page
                    spacing=10  # Space between text and divider
                ),
                
                # Wrap the welcome message and buttons in a single container and center it horizontally
                ft.Container(
                    content=ft.Column(
                        controls=[
                            # Welcome message
                            ft.Container(
                              ft.Text("Welcome to SMOG!", size=20, weight="bold", color="blue"),
                              padding=ft.padding.only(bottom=10)  # Add space below the welcome message
                            ),
                            # Stacked buttons
                            ft.Column(
                                controls=[
                                    ft.ElevatedButton("Difficulty 1", on_click=lambda e: print("Option 1 clicked")),
                                    ft.ElevatedButton("Difficulty 2", on_click=lambda e: print("Option 2 clicked")),
                                    ft.ElevatedButton("Difficulty 3", on_click=lambda e: print("Option 3 clicked")),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,  # Space between buttons
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
