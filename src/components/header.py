import flet as ft

def HeaderBar(router):
    def handle_back(e):
        router.navigate_back()

    back_button = ft.IconButton(
        icon=ft.Icons.ARROW_CIRCLE_LEFT_OUTLINED,
        icon_size=35,
        icon_color=ft.Colors.GREY_900,
        on_click=handle_back,
        alignment=ft.alignment.top_right
    )

    return ft.Container(
        content=ft.Row(
            controls=[
                back_button
            ],
        ),
        padding=ft.padding.only(top=20)
    )