import flet as ft

# Sample quiz questions
quiz_data = [
    {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4"},
    {"question": "What is the capital of France?", "options": ["Berlin", "Paris", "Rome", "Madrid"], "answer": "Paris"},
    {"question": "What is 5 * 3?", "options": ["15", "10", "20", "25"], "answer": "15"},
    {"question": "What is the largest planet in our solar system?", "options": ["Earth", "Mars", "Jupiter", "Saturn"], "answer": "Jupiter"},
    {"question": "What is the powerhouse of the cell?", "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi Apparatus"], "answer": "Mitochondria"},
]

def show_dif1_page(page: ft.Page, router):
    page.clean()

    # Variables for progress and score
    quiz_index = 0  # Start at question 0
    score = 0  # Start with score 0
    quiz_completed = False  # Track if the quiz is completed

    # Function to load a question
    def load_question():
        nonlocal quiz_index, score
        if quiz_index < len(quiz_data):
            question_data = quiz_data[quiz_index]
            question = question_data["question"]
            options = question_data["options"]
            answer = question_data["answer"]
            
            display_question(question, options, answer)
        else:
            display_results()  # If quiz is complete, show results

    # Function to display the question and options
    def display_question(question, options, answer):
        def handle_answer(e):
            nonlocal quiz_index, score, quiz_completed
            # Controleer of de quiz al voltooid is
            if quiz_completed:
                print("Quiz is already completed. Ignoring further interactions.")
                return  # Stop verdergaan als de quiz voltooid is

            if e.control.data == answer:
                score += 1
                result_text.value = "Correct! 🎉"
                result_text.color = "green"
            else:
                result_text.value = "Wrong! 😞"
                result_text.color = "red"

            quiz_index += 1
            progress_bar.value = (quiz_index / len(quiz_data))
            page.update()

            # Controleer of de quiz is voltooid
            if quiz_index < len(quiz_data):
                load_question()  # Laad de volgende vraag
            else:
                quiz_completed = True  # Zet de quiz op voltooid
                show_result_button.visible = True  # Toon de knop om naar de resultaten te gaan
                result_text.value = ""  # Verberg de resultaattekst
                page.update()

        progress_bar.value = (quiz_index / len(quiz_data))

        # Zet de vraag en opties
        question_text.value = question
        options_container.controls = []

        # Dynamisch de knoppen maken, met een flexibele verdeling van ruimte
        for i in range(0, len(options), 2):
            options_row = ft.Row(
                controls=[
                    ft.ElevatedButton(
                        text=options[i], 
                        on_click=handle_answer, 
                        data=options[i],
                        width=200,  # Geef de knoppen een beperkte breedte
                        height=70,  # Verhoog de hoogte van de knoppen
                        bgcolor="lightblue",  # Geef de knoppen een kleurtje
                        expand=True  # Zorg ervoor dat ze zich aanpassen aan de ruimte
                    ),
                    ft.ElevatedButton(
                        text=options[i + 1] if i + 1 < len(options) else "", 
                        on_click=handle_answer, 
                        data=options[i + 1] if i + 1 < len(options) else "",
                        width=200,  # Geef de knoppen een beperkte breedte
                        height=70,  # Verhoog de hoogte van de knoppen
                        bgcolor="lightblue",  # Geef de knoppen een kleurtje
                        expand=True  # Zorg ervoor dat ze zich aanpassen aan de ruimte
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
            options_container.controls.append(options_row)
        
        result_text.value = ""  # Reset de resultaat tekst voor het volgende antwoord
        page.update()

    # Function for the results
    def display_results():
        print("display_results called")  # Debugging om te controleren of deze functie wordt aangeroepen
        page.clean()  # Maak de pagina leeg

        # Voeg de resultaten toe aan de pagina
        page.add(
            ft.Column(
                controls=[
                    ft.Text(f"Quiz completed! Your score: {score}/{len(quiz_data)}", size=24),
                    ft.ElevatedButton("Back to Difficulty Selection", on_click=lambda e: router.navigate("/learn")),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )
        )
        page.update()  # Forceer een update van de pagina

    # UI elementen voor de quiz
    progress_bar = ft.ProgressBar(width=300, height=20,bgcolor='#2fed98',  # Stel de achtergrondkleur in
        border_radius=10, )  # Verhoog de hoogte van de voortgangsbalk
    progress_bar.color = "green"  # Zet de voortgangsbalk op groen
    question_text = ft.Text(size=20, weight="bold")
    options_container = ft.Column(spacing=10)
    result_text = ft.Text(size=16)

    # Knop om naar resultatenpagina te gaan (zichtbaar na de laatste vraag)
    show_result_button = ft.ElevatedButton(
        text="Go to Results",
        on_click=lambda e: router.navigate(f"/results/{score}/{len(quiz_data)}"),
        visible=False  # Verberg de knop eerst
    )

    # Back button (top left corner)
    back_button = ft.ElevatedButton(
        text="Back",
        on_click=lambda e: router.navigate("/home"),
        bgcolor="lightgray"
    )

    # Account icon button (top right corner)
    account_icon_button = ft.IconButton(
        icon=ft.icons.PERSON,
        tooltip="Account Settings",
        on_click=lambda e: router.navigate("/account")
    )
    

    # Layout: Camera boven en quiz beneden
    content = ft.Column(
        controls=[
            ft.Row(
                controls=[back_button, account_icon_button],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=10,
            ),
            ft.Container(
                content=ft.Text("Camera feed here (placeholder)", size=18, color="black"),
                height=300,  # Gebruik de bovenste helft van het scherm
                alignment=ft.alignment.center,
                bgcolor="lightblue"
            ),
            
            # Verklein de padding om de vraag dichter bij de progressie balk te plaatsen
            ft.Container(
                content=progress_bar,
                padding=ft.padding.symmetric(vertical=5),  # Minder ruimte tussen vraag en progressie
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        question_text,
                        ft.Container(height=60),
                        options_container,
                        result_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    
                    spacing=0,  # Verklein de ruimte tussen vraag en opties
                ),
                expand=True,  # Gebruik de onderste helft van het scherm
                padding=ft.padding.all(20),
                bgcolor="white",
            ),
            show_result_button  # Voeg de knop toe aan de layout
        ],
        expand=True,
    )

    # Start de quiz
    load_question()

    # Retourneer de view voor de router
    return ft.View(
        route="/difficulty1",
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
