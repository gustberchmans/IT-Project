import flet as ft

class Snackbar(ft.UserControl):
    def __init__(self, message: str, duration: int = 3000, action: str = None, action_callback=None):
        super().__init__()
        self.message = message
        self.duration = duration
        self.action = action
        self.action_callback = action_callback

    def build(self):
        return ft.Snackbar(
            content=ft.Text(self.message),
            duration=self.duration,
            action=self.action,
            on_action=self.action_callback
        )

def show_snackbar(page: ft.Page, message: str, duration: int = 3000, action: str = None, action_callback=None):
    snackbar = Snackbar(message, duration, action, action_callback)
    page.snackbar = snackbar.build()
    page.snackbar.open()
    page.update()