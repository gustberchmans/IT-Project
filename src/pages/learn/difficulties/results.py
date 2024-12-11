import flet as ft

def show_results_page(page: ft.Page, router, score: str, total_questions: str):
    # Converteer strings naar integers
    try:
        score = int(score)
        total_questions = int(total_questions)
    except ValueError:
        # Fallback als de conversie niet werkt
        score = 0
        total_questions = 1  # Om een divisie door nul te voorkomen

    # Bereken percentage
    percentage = (score / total_questions) * 100

    # Maak een view aan voor de resultatenpagina
    view = ft.View(
        route=f"/results/{score}/{total_questions}",
        controls=[
            # Bovenste navigatiebalk
            ft.Row(
                controls=[
                    ft.ElevatedButton("Home", on_click=lambda e: router.navigate("/home")),
                    ft.IconButton(icon=ft.icons.PERSON, on_click=lambda e: router.navigate("/account")),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=False,  # Deze balk blijft bovenaan
            ),
            # Resultatenweergave
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Dynamische logica voor icoon en tekst
                        ft.Icon(
                            name=ft.icons.CHECK_CIRCLE if percentage >= 50 else ft.icons.CANCEL,
                            size=100,
                            color="green" if percentage >= 50 else "red"
                        ),
                        ft.Text(
                            "Congratulations!" if percentage >= 50 else "Better luck next time!",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color="green" if percentage >= 50 else "red",
                            text_align=ft.TextAlign.CENTER  # Gecentreerde tekst
                        ),
                        ft.Divider(height=20, thickness=2),
                        # Score informatie
                        ft.Text(
                            f"Quiz completed! Your score: {score}/{total_questions}",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER  # Gecentreerde tekst
                        ),
                        ft.Divider(height=20, thickness=2),
                        ft.Text(
                            "Thank you for participating in the quiz!",
                            size=18,
                            text_align=ft.TextAlign.CENTER  # Gecentreerde tekst
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,  # Centreer de inhoud verticaal
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centreer de inhoud horizontaal
                    spacing=20,  # Voeg wat ruimte toe tussen elementen
                ),
                alignment=ft.alignment.center,  # Centreer de container op het scherm
                expand=True,  # Zorg ervoor dat het volledig beschikbare scherm wordt gebruikt
            ),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,  # Centreer alles verticaal
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centreer alles horizontaal
    )
    return view
