import flet as ft
from services.firebase import add_score, get_current_user, get_videos, update_progress
from utils.helpers import extract_word_from_url



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
        border_radius=10,
        alignment=ft.alignment.center,
    )

def show_d1l2_page(page: ft.Page, router):
    page.clean()
    
    # Game state
    state = {
        "video_index": 0,
        "score": 0,
        "videos": get_videos()
    }
    
    # Process videos
    video_data = [{
        "video_url": url,
        "word": extract_word_from_url(url)
    } for url in state["videos"]]
    
    if not video_data:
        return ft.View(
            route="/video_word_game",
            controls=[ft.Text("No videos available.", size=24)]
        )

    # UI Components
    result_text = ft.Text(size=16)
    user_input = ft.TextField(
        label="Your Answer",
        hint_text="Type the word you see in the video",
        width=400,
        text_size=16,
        border_radius=8,
        autofocus=True
    )
    content_container = ft.Container(padding=20, expand=True)

    # Add a new state variable to track attempts
    state["attempts"] = 0

    def show_results():
        user_id = get_current_user()
        update_progress(user_id, "difficulty1", "d1l2", 1)
        add_score(user_id, state["score"], "video_word_game", len(video_data))
        
        content_container.content = ft.Column(
            controls=[
                ft.Text(
                    f"Game completed! Your score: {state['score']}/{len(video_data)}",
                    size=28,
                    weight=ft.FontWeight.BOLD
                ),
                ft.ElevatedButton(
                    "Back to Home",
                    on_click=lambda _: router.navigate("/home"),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
        page.update()

    def check_answer(e):
        current_word = video_data[state["video_index"]]["word"]
        user_answer = user_input.value.strip().lower()
        
        if user_answer == current_word.lower():
            state["score"] += 1
            result_text.value = "Correct! 🎉"
            result_text.color = ft.Colors.GREEN
            state["video_index"] += 1
            state["attempts"] = 0  # Reset attempts for the next question
            user_input.value = ""
            page.update()
            if state["video_index"] < len(video_data):
                load_video()
            else:
                show_results()
        else:
            state["attempts"] += 1
            attempts_left = max(0, 3 - state["attempts"])  # Ensure attempts don't go negative
            result_text.value = f"Incorrect! Attempts left: {attempts_left}"
            result_text.color = ft.Colors.RED
            user_input.value = ""
            page.update()

            if state["attempts"] >= 3:
                # Ensure only one skip button is added
                if not any(isinstance(control, ft.ElevatedButton) and control.text == "Skip" for control in content_container.content.controls):
                    result_text.value += " You can choose to skip this question."
                    skip_button = ft.ElevatedButton(
                        "Skip",
                        on_click=lambda _: skip_question(),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            bgcolor=ft.Colors.ORANGE,
                            color=ft.Colors.WHITE,
                        ),
                        width=400,
                        height=50
                    )
                    content_container.content.controls.append(skip_button)
                    page.update()

    def skip_question():
        state["video_index"] += 1
        state["attempts"] = 0  # Reset attempts for the next question
        user_input.value = ""
        page.update()
        if state["video_index"] < len(video_data):
            load_video()
        else:
            show_results()

    def load_video():
        if state["video_index"] >= len(video_data):
            show_results()
            return

        video_url = video_data[state["video_index"]]["video_url"]
        
        content_container.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "Watch the video and type the word you see:",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    margin=ft.margin.only(bottom=10)
                ),
                create_video_player(video_url),
                ft.Container(
                    content=ft.Column([
                        user_input,
                        ft.ElevatedButton(
                            "Submit",
                            on_click=check_answer,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                bgcolor=ft.Colors.BLUE,
                                color=ft.Colors.WHITE,
                            ),
                            width=400,
                            height=50
                        )
                    ]),
                    margin=ft.margin.only(top=10)
                ),
                result_text
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
        page.update()

    # Header with navigation
    header = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Back",
                on_click=lambda _: router.navigate("/home")
            ),
            ft.IconButton(
                icon=ft.Icons.PERSON,
                tooltip="Account Settings",
                on_click=lambda _: router.navigate("/account")
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # Initialize first video
    load_video()

    return ft.View(
        route="/video_word_game",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[header, content_container],
                    expand=True
                ),
                padding=20,
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
