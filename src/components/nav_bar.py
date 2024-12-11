import flet as ft

class NavBar(ft.UserControl):
    def __init__(self, router, active_route: str):
        super().__init__()
        self.router = router
        self.active_route = active_route

    def build(self):
        return ft.Container(
            content=ft.Row(
                controls=[
                    self._create_nav_button("", "/home", ft.icons.HOME),
                    self._create_nav_button("", "/learn", ft.icons.SCHOOL),
                    self._create_nav_button("", "/translate", ft.icons.TRANSLATE),
                    self._create_nav_button("", "/account", ft.icons.PERSON),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                spacing=0
            ),
            padding=5,
            expand=True,
            alignment=ft.alignment.bottom_center,
            border=ft.Border(
                top=ft.BorderSide(width=1, color=ft.colors.GREY_300)
            ),
            border_radius=ft.BorderRadius(3, 3, 0, 0)
        )

    def _create_nav_button(self, text: str, route: str, icon: str) -> ft.Control:
        is_active = self.active_route == route
        return ft.IconButton(
            icon=icon,
            icon_size=40,
            icon_color=ft.colors.BLUE if is_active else ft.colors.BLACK,
            on_click=lambda _: self.router.navigate(route),
            
        )