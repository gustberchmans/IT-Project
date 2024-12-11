import flet as ft
from router import Router
from pages.login import show_login_page
from pages.register import show_register_page
from pages.translate import show_translate_page
from pages.learn.learn import show_learn_page
from pages.learn.difficulties.diff1 import show_dif1_page
from pages.account import show_account_page
from pages.home import show_home_page

def main(page: ft.Page):
    router = Router(page)

    router.add_route("/login", lambda p: show_login_page(p, router))
    router.add_route("/register", lambda p: show_register_page(p, router))
    router.add_route("/translate", lambda p: show_translate_page(p, router))
    router.add_route("/learn", lambda p: show_learn_page(p, router))
    router.add_route("/difficulty1", lambda p: show_dif1_page(p, router))
    router.add_route("/account", lambda p: show_account_page(p, router))
    router.add_route("/home", lambda p: show_home_page(p, router))
    page.title = "GebarenTool"
    page.theme_mode = ft.ThemeMode.LIGHT
    

    router.navigate("/login")   

ft.app(target=main)