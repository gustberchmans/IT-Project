import flet as ft
from typing import Optional, List

class BaseLayout(ft.UserControl):
    def __init__(
        self,
        content: ft.Control,
        nav_bar: Optional[ft.Control] = None,
        padding: int = 10,
        spacing: int = 10,
        title: Optional[str] = None
    ):
        super().__init__()
        self.content = content
        self.nav_bar = nav_bar
        self.padding = padding
        self.spacing = spacing
        self.title = title

    def build(self):
        layout_controls: List[ft.Control] = []
        
        if self.title:
            layout_controls.append(
                ft.Container(
                    content=ft.Text(self.title, size=24, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(bottom=20)
                )
            )
        
        layout_controls.append(self.content)
        
        if self.nav_bar:
            layout_controls.append(self.nav_bar)

        return ft.Container(
            content=ft.Column(
                controls=layout_controls,
                spacing=self.spacing,
                expand=True
            ),
            padding=self.padding
        )