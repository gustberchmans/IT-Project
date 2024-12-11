import flet as ft
from typing import Dict, Callable, Optional
import re

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
        matched_route, params = self.match_route(route)
        if not matched_route:
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
        view = self.routes[matched_route](self.page, **params)
        if view is None:
            raise ValueError(f"Route handler for {route} returned None")

        self.page.views.pop()
        self.page.views.append(view)
        self.page.update()

    def navigate_back(self):
        if self.history:
            previous_route = self.history.pop()
            self.navigate(previous_route)
        else:
            print("No previous route to navigate back to.")

    def match_route(self, route: str):
        for path in self.routes:
            pattern = re.sub(r'{\w+}', r'([^/]+)', path)
            match = re.match(f'^{pattern}$', route)
            if match:
                param_names = re.findall(r'{(\w+)}', path)
                params = {name: value for name, value in zip(param_names, match.groups())}
                return path, params
        return None, {}

    def _handle_route_change(self, route):
        self.navigate(route.route)

    def _handle_view_pop(self, view):
        if self.history:
            self.navigate(self.history.pop())
        else:
            self.page.views.pop()
            top_view = self.page.views[-1]
            self.page.go(top_view.route)