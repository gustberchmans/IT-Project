import flet as ft
from services.firebase import add_score, get_current_user, update_progress, get_videos
from utils.helpers import extract_word_from_url
import random
import time
from components.header import HeaderBar

def fetch_videos_and_create_questions():
    videos = get_videos()  # Fetch videos from the bucket
    # Randomize the video order
    random.shuffle(videos)
    questions = []
    
    # Common Dutch sign language words to use as distractors
    dutch_signs = ["Hallo", "Dag", "Eten", "Drinken", "Eerst", "Dank je wel", 
                  "Goedemorgen", "Tot ziens", "Alsjeblieft", "Sorry"]
    
    for video_url in videos:
        correct_answer = extract_word_from_url(video_url)
        
        # Create options: include correct answer and exactly 3 random distractors
        options = [correct_answer]
        available_options = [word for word in dutch_signs if word != correct_answer]
        random_options = random.sample(available_options, 3)  # Get exactly 3 random options
        options.extend(random_options)
        
        # Shuffle the options to randomize the correct answer position
        random.shuffle(options)
        
        question = {
            "question": "Which gesture is shown?",
            "options": options,
            "answer": correct_answer
        }
        questions.append(question)

    return questions, videos

# Update quiz_data with questions from videos
quiz_data, videos = fetch_videos_and_create_questions()

def show_d1l1_page(page: ft.Page, router):
    global lives_left
    lives_left = 3
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
        
             # If quiz is complete, show results

    # Function to display the question and options
    def display_question(question, options, answer):
        nonlocal lives_text
        
        lives_text.value = f"Lives left: {'❤️' * lives_left}"
        
        def handle_answer(e):
            nonlocal quiz_index, score, quiz_completed
            global lives_left

            if quiz_completed:
                return

            if e.control.data == answer:  # Correct antwoord
                score += 1
                if quiz_index == len(quiz_data) - 1:  # Laatste vraag
                    quiz_completed = True  # Markeer quiz als voltooid
                    result_text.value = "Quiz Complete! Going to results..."
                    page.update()
                    time.sleep(2)

                    # Opslaan van de score en navigeren naar de resultatenpagina
                    user_id = get_current_user()
                    add_score(user_id, score, "difficulty1", len(quiz_data))
                    update_progress(user_id, "difficulty1", "d1l1", 1)
                    router.navigate(f"/results/{score}/{len(quiz_data)}")
                else:
                    result_text.value = "Correct! ✅"
                    result_text.color = "green"
                    page.update()
                    time.sleep(1)
                    quiz_index += 1
                    load_question()

            else:  # Verkeerd antwoord
                if lives_left > 0:  # Controleer of er levens over zijn
                    lives_left -= 1
                    lives_text.value = f"Lives left: {'❤️' * lives_left}"
                    page.update()

                    if lives_left == 0:  # Geen levens meer
                        quiz_completed = True  # Markeer quiz als voltooid
                        result_text.value = "No lives left! Going to results..."
                        page.update()
                        

                        # Navigeren naar de resultatenpagina
                        user_id = get_current_user()
                        add_score(user_id, score, "d1l1", len(quiz_data))
                        router.navigate(f"/results/{score}/{len(quiz_data)}")
                    else:
                        result_text.value = "Wrong! ❌"
                        result_text.color = "red"
                        page.update()
                        
                        result_text.value = ""
                        page.update()
                else:
                    print("[DEBUG] Er zijn al geen levens mee")

            # Update voortgangsbalk
            progress_bar.value = (quiz_index / len(quiz_data))
            page.update()


        progress_bar.value = (quiz_index / len(quiz_data))

        # Get current video URL from quiz data
        current_video = videos[quiz_index]
        video_container.content = create_video_player(current_video)
        
        question_text.value = question
        options_container.controls = []

        for i in range(0, len(options), 2):
            options_row = ft.Row(
                controls=[
                    ft.ElevatedButton(
                        text=options[i], 
                        on_click=handle_answer, 
                        data=options[i],
                        width=200,
                        height=80,
                        bgcolor="LightBlue",
                        color="white",
                        expand=True,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=15),
                        )
                    ),
                    ft.ElevatedButton(
                        text=options[i + 1] if i + 1 < len(options) else "", 
                        on_click=handle_answer, 
                        data=options[i + 1] if i + 1 < len(options) else "",
                        width=200,
                        height=80,
                        bgcolor="LightBlue",  # Darker blue
                        color="white",
                        expand=True,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=15),
                        )
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
            options_container.controls.append(options_row)
        
        result_text.value = ""
        page.update()

    # Function for the results
    

    # UI elements with improved styling
    progress_bar = ft.ProgressBar(
        width=350, 
        height=15, 
        bgcolor='#E3F2FD',
        color="#2196F3",
        border_radius=10
    )
    
    question_text = ft.Text(
        value="What gesture is shown?",  # Updated question text
        size=20,
        weight="bold",
        color="#1565C0",
        text_align=ft.TextAlign.CENTER
    )
    
    options_container = ft.Column(spacing=10)
    result_text = ft.Text(size=16)
    lives_text = ft.Text(f"Lives left: ❤️❤️❤️", size=16, color="#1565C0")

    video_container = ft.Container(
        height=300,  # Increased from 300
        alignment=ft.alignment.center,
    )

    # Update the content layout
    content = ft.Column(
        controls=[
            HeaderBar(router),
            ft.Container(  # Progress section - moved to top
                content=ft.Column([
                    ft.Row(
                        [progress_bar],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=5),
                    ft.Row(
                        [lives_text],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ]),
                padding=ft.padding.only(top=10),
                alignment=ft.alignment.center,
            ),
            ft.Container(  # Video section - moved below progress bar
                content=video_container,
            ),
            ft.Container(  # Question section
                content=ft.Column(
                    controls=[
                        question_text,
                        ft.Container(height=15),
                        options_container,
                        ft.Container(height=5),
                        result_text,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=0,
                ),
                expand=True,
                margin=ft.margin.only(left=10, right=10),
            ),
        ],
        expand=True,
        spacing=0,
    )

    # Add the create_video_player function
    def create_video_player(video_url):
        return ft.Container(
            content=ft.Video(
                playlist=[ft.VideoMedia(video_url)],
                playlist_mode=ft.PlaylistMode.LOOP,
                aspect_ratio=16/9,
                volume=0,
                show_controls=False,
                autoplay=True,
                filter_quality=ft.FilterQuality.LOW,
            ),
            height=300,
            width=500,
            alignment=ft.alignment.center,
        )

    load_question()

    return ft.View(
        route="/difficulty1",
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
