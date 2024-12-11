import flet as ft

def show_results_page(page: ft.Page, router, score: int, total_questions: int):
    # Maak een view aan voor de resultatenpagina
    view = ft.View(
        route=f"/results/{score}/{total_questions}",
        controls=[
            ft.Row(
                controls=[
                    ft.ElevatedButton("Home", on_click=lambda e: router.navigate("/home")),
                    ft.IconButton(icon=ft.icons.PERSON, on_click=lambda e: router.navigate("/account")),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            ),
            ft.Column(
                controls=[
                    ft.Text(f"Quiz completed! Your score: {score}/{total_questions}", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20, thickness=2),
                    ft.Text("Thank you for participating in the quiz!", size=18),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return view