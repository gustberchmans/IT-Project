import flet as ft

def HeaderBar(router):
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda _: router.go("/"),
                    icon_color=ft.colors.BLACK,
                ),
                ft.Text(
                    "Live translator start",
                    size=16,
                    weight=ft.FontWeight.W_500,
                ),
            ],
        ),
        padding=10,
    )
