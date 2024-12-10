import flet as ft

def show_snackbar(page: ft.Page, message: str, color: str = "green"):
    """
    Shows a snackbar with the given message and color at the top of the screen.
    Args:
        page: The Flet page instance
        message: Message to display
        color: Color of the snackbar (default: green for success)
    """
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=color,
        behavior=ft.SnackBarBehavior.FLOATING,
        margin=ft.margin.only(top=20, left=20, right=20),
        duration=3000,
    )
    page.snack_bar.open = True
    page.update()

def show_error_snackbar(page: ft.Page, message: str):
    """Convenience method for error messages"""
    show_snackbar(page, message, "red")

def show_success_snackbar(page: ft.Page, message: str):
    """Convenience method for success messages"""
    show_snackbar(page, message, "green") 