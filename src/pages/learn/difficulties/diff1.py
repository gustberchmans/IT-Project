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
            display_results()

    # Function to display the question and options
    def display_question(question, options, answer):
        def handle_answer(e):
            nonlocal quiz_index, score, quiz_completed
            if quiz_completed:
                return
            if e.control.data == answer:
                score += 1
                result_text.value = "Correct! 🎉"
                result_text.color = "green"
            else:
                result_text.value = "Wrong! 😞"
                result_text.color = "red"
                
            quiz_index += 1
            page.update()
            
            if quiz_index < len(quiz_data):
                load_question()
            else:
                quiz_completed = True
                display_results()

        progress_bar.value = (quiz_index / len(quiz_data))

        # Set the question and options
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

        # Add a flag to track if the quiz is completed
        quiz_completed = False

    # Function for the results
    def display_results():
        page.clean()
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

    # UI elements for the quiz
    progress_bar = ft.ProgressBar(width=200)
    question_text = ft.Text(size=20, weight="bold")
    options_container = ft.Column(spacing=10)
    result_text = ft.Text(size=16)

    # Back button (top left corner)
    back_button = ft.ElevatedButton(
        text="Back",
        on_click=lambda e: router.navigate("/learn"),
        bgcolor="lightgray"
    )

    # Account settings button (top right corner)
    account_settings_button = ft.IconButton(
        icon=ft.icons.PERSON,
        on_click=lambda e: router.navigate("/account"),
        bgcolor="lightgray"
    )

    # Layout: Camera above and quiz below
    content = ft.Column(
        controls=[
            ft.Row(
                controls=[back_button, account_settings_button],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=10,
            ),
            ft.Container(
                content=ft.Text("Camera feed here (placeholder)", size=18, color="gray"),
                height=300,  # Use the top half of the screen
                alignment=ft.alignment.center,
                bgcolor="lightblue"
            ),
            ft.Container(
                content=progress_bar,
                padding=ft.padding.symmetric(vertical=10),  # Add some space
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
                expand=True,  # Use the bottom half of the screen
                padding=ft.padding.all(20),
                bgcolor="white",
            )
        ],
        expand=True,
    )

    # Start the quiz
    load_question()

    # Return the view for the router
    return ft.View(
        route="/difficulty1",
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
