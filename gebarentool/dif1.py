import flet as ft


from account import show_page3






# Voorbeeld van quizvragen
quiz_data = [
    {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4"},
    {"question": "What is the capital of France?", "options": ["Berlin", "Paris", "Rome", "Madrid"], "answer": "Paris"},
    {"question": "What is 5 * 3?", "options": ["15", "10", "20", "25"], "answer": "15"},
    {"question": "What is the largest planet in our solar system?", "options": ["Earth", "Mars", "Jupiter", "Saturn"], "answer": "Jupiter"},
    {"question": "What is the powerhouse of the cell?", "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi Apparatus"], "answer": "Mitochondria"},
    
]

# Functie voor de quizpagina
def show_dif1_page(page, show_main_page, show_page3):
    from leerTool import show_page1
    
    
    page.clean()

    # Variabelen voor voortgang en score
    quiz_index = 0  # Begin bij vraag 0
    score = 0  # Begin bij score 0

    # Functie om een vraag te laden
    def load_question():
        nonlocal quiz_index, score
        if quiz_index < len(quiz_data):
            question_data = quiz_data[quiz_index]
            question = question_data["question"]
            options = question_data["options"]
            answer = question_data["answer"]
            
            display_question(question, options, answer)
        else:
            display_results()

    # Functie om de vraag en opties weer te geven
    def display_question(question, options, answer):
        def handle_answer(e):
            nonlocal quiz_index, score
            if e.control.data == answer:
                score += 1
                result_text.value = "Correct! 🎉"
                result_text.color = "green"
            else:
                result_text.value = "Wrong! 😞"
                result_text.color = "red"
                
            
            quiz_index += 1
            page.update()
            load_question()
        progress_bar.value = (quiz_index / len(quiz_data))

        # Stel de vraag en opties in
        question_text.value = question
        options_container.controls = []
        for i in range(0, len(options), 2):
            options_row = ft.Row(
                controls=[
                    ft.ElevatedButton(text=options[i], on_click=handle_answer, data=options[i]),
                    ft.ElevatedButton(text=options[i+1] if i+1 < len(options) else "", on_click=handle_answer, data=options[i+1] if i+1 < len(options) else "")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
            options_container.controls.append(options_row)
        result_text.value = ""
        page.update()

    # Functie voor de resultaten
    def display_results():
        page.clean()
        page.add(
            ft.Column(
                controls=[
                    ft.Text(f"Quiz completed! Your score: {score}/{len(quiz_data)}", size=24),
                    ft.ElevatedButton("Back to Difficulty Selection", on_click=lambda e: show_page1(page, show_main_page, show_page3)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )
        )

    # UI-elementen voor de quiz
    progress_bar = ft.ProgressBar(width=200)
    question_text = ft.Text(size=20, weight="bold")
    options_container = ft.Column(spacing=10)
    result_text = ft.Text(size=16)

    # Layout: Camera boven en quiz beneden
    page.add(
        ft.Column(
            controls=[
                
                # Placeholder voor de camera
                ft.Container(
                    content=ft.Text("Camera feed here (placeholder)", size=18, color="gray"),
                    height=300,  # Gebruik de bovenste helft van het scherm
                    alignment=ft.alignment.center,
                    bgcolor="lightblue"
                ),
                ft.Container(
                    content=progress_bar,
                    padding=ft.padding.symmetric(vertical=10),  # Voeg wat ruimte toe
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            question_text,
                            options_container,
                            result_text,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    expand=True,  # Gebruik de onderste helft van het scherm
                    padding=ft.padding.all(20),
                    bgcolor="white",
                )
                
            ],
            expand=True,
        )
    )

    # Start de quiz
    load_question()