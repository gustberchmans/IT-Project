import flet as ft
from typing import Dict, Callable, Optional

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes: Dict[str, Callable] = {}
        self.current_route: Optional[str] = None
        self.history: list = []
        
        self.page.on_route_change = self._handle_route_change
        self.page.on_view_pop = self._handle_view_pop

    def add_route(self, route: str, handler: Callable):
        self.routes[route] = handler

    def navigate(self, route: str, **kwargs):
        if route not in self.routes:
            raise ValueError(f"Route {route} not found")

        if self.current_route:
            self.history.append(self.current_route)

        self.current_route = route
        
        # Show loading state
        self.page.views.append(
            ft.View(
                route=route,
                controls=[
                    ft.ProgressRing(width=40, height=40)
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.update()

        # Render new route
        view = self.routes[route](self.page, **kwargs)
        if view is None:
            raise ValueError(f"Route handler for {route} returned None")

        self.page.views.pop()
        self.page.views.append(view)
        self.page.update()

    def _handle_route_change(self, route):
        self.navigate(route.route)

    def _handle_view_pop(self, view):
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)