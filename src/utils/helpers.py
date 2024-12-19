import re
from typing import Any, Dict, List
import flet as ft
import urllib.parse

def is_valid_email(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def format_timestamp(timestamp: float) -> str:
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    return [item for sublist in nested_list for item in sublist]

def dict_to_query_string(params: Dict[str, Any]) -> str:
    return '&'.join(f"{key}={value}" for key, value in params.items())

def generate_random_string(length: int) -> str:
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def calculate_average(numbers: List[float]) -> float:
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

def show_snackbar(page, message: str, color: str = "green"):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=color,
        behavior=ft.SnackBarBehavior.FLOATING,
        margin=ft.margin.only(top=20, left=20, right=20),
        duration=1500
    )
    page.snack_bar.open = True
    page.update()

def show_error_snackbar(page, message: str):
    show_snackbar(page, message, "red")

def show_success_snackbar(page, message: str):
    show_snackbar(page, message, "green")

def extract_word_from_url(url):
    filename = urllib.parse.urlparse(url).path.split('/')[-1]
    word, _ = filename.split('.')
    return word