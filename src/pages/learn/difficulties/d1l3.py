import threading
import time
import flet as ft
from services.firebase import add_score, get_current_user, get_videos, update_progress
import urllib

def show_d1l3_page(page: ft.Page, router):
    page.clean()

    video_index = 0  # Start at the first video
    score = 0  # Keep track of the score
    user_input = ft.TextField(label="Your Answer", hint_text="Type the word here", width=300)
    result_text = ft.Text(size=16)
    videos = get_videos()  # Fetch video URLs from Firebase

    if not videos or len(videos) == 0:
        page.add(ft.Text("No videos found.", size=24))
        return

    # Extract word from video filename
    def extract_word_from_url(url):
        parsed_url = urllib.parse.urlparse(url)
        filename = parsed_url.path.split('/')[-1]  # Extract the last part of the path
        word, _ = filename.split('.')  # Split filename by the '.' and get the first part
        print(word)
        return word

    # Create video data with extracted words
    video_data = [
        {
            "video_url": url,
            "word": extract_word_from_url(url)
        } for url in videos
    ]

    # Function to load the current video (using threading)
    def load_video():
        nonlocal video_index
        if video_index < len(video_data):
            video_url = video_data[video_index]["video_url"]
            word = video_data[video_index]["word"]
            # Wait for 3 seconds before starting the video
            threading.Thread(target=start_video, args=(video_url, word)).start()
        else:
            display_results()

    # Function to start the video after a 3-second delay
    def start_video(video_url, word):
        # Wait for 3 seconds
        time.sleep(3)  # Delay for 3 seconds
        display_video(video_url, word)

    # Function to display a video and accept input
    def display_video(video_url, word):
        def check_answer(e):
            nonlocal video_index, score
            if user_input.value.strip().lower() == word.lower():
                result_text.value = "Correct! 🎉"
                result_text.color = "green"
                score += 1
            else:
                result_text.value = f"Wrong! The correct word was: {word}"
                result_text.color = "red"

            video_index += 1
            user_input.value = ""  # Clear the input field
            page.update()  # Update the page to show the result
            load_video()

        # Clear and display the video and input field
        content_container.controls.clear()
        content_container.controls.append(
            ft.Column(
                controls=[
                    ft.Text("Watch the video and type the word:", size=20),
                    ft.Container(
                        content=ft.Video(
                            playlist=[ft.VideoMedia(video_url)],
                            playlist_mode=ft.PlaylistMode.LOOP,
                            aspect_ratio=16/9,
                            volume=0,
                            autoplay=True,
                            
                            filter_quality=ft.FilterQuality.LOW,  # Medium quality for faster loading
                        ),
                        height=300,
                        width=400,
                        alignment=ft.alignment.center,
                    ),
                    user_input,
                    ft.Container(
                        content=ft.ElevatedButton("Submit", on_click=check_answer),
                        alignment=ft.alignment.bottom_right,
                        padding=ft.padding.only(right=20, bottom=20),
                    ),
                    result_text,
                ]
            )
        )
        page.update()

    # Function to display the final results
    def display_results():
        user_id = get_current_user()
        update_progress(user_id, "difficulty1", "d1l3", 1)
        router.navigate(f"/results/{score}/{len(video_data)}")
        page.clean()
        user_id = get_current_user()
        add_score(user_id, score, "video_word_game", len(video_data))

        page.add(
            ft.Column(
                controls=[
                    ft.Text(f"Game completed! Your score: {score}/{len(video_data)}", size=24),
                    ft.ElevatedButton("Back to Home", on_click=lambda e: router.navigate("/home"))
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        )
        page.update()

    # Back button
    back_button = ft.ElevatedButton(
        text="Back",
        on_click=lambda e: router.navigate("/home"),
        bgcolor="lightgray"
    )

    # Account icon button
    account_icon_button = ft.IconButton(
        icon=ft.Icons.PERSON,
        tooltip="Account Settings",
        on_click=lambda e: router.navigate("/account")
    )

    # Main container for the page content
    content_container = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
        spacing=10
    )

    # Layout
    content = ft.Column(
        controls=[
            ft.Row(
                controls=[back_button, account_icon_button],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=10
            ),
            content_container,
            result_text
        ],
        expand=True
    )

    # Load the first video
    load_video()

    # Return the view for the router
    return ft.View(
        route="/video_word_game",
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
