import flet as ft
from services.firebase import add_score, get_current_user

# Placeholder data for video and corresponding words
video_data = [
    {"video_url": "", "word": "cat"},
    {"video_url": "", "word": "dog"},
    {"video_url": "", "word": "bird"}
]

def show_d1l2_page(page: ft.Page, router):
    page.clean()

    video_index = 0  # Start at the first video
    score = 0  # Keep track of the score
    user_input = ft.TextField(label="Your Answer", hint_text="Type the word here", width=300)
    result_text = ft.Text(size=16)

    # Function to load a placeholder for the video
    def load_video():
        nonlocal video_index
        if video_index < len(video_data):
            word = video_data[video_index]["word"]
            display_video_placeholder(word)
        else:
            display_results()

    # Function to display a placeholder and word initially
    def display_video_placeholder(word):
        def proceed_to_typing(e):
            nonlocal video_index
            result_text.value = ""  # Reset result text
            content_container.controls.clear()
            content_container.controls.append(
                ft.Column(
                    controls=[
                        ft.Text("Imagine the video is playing and type the word:", size=20),
                        ft.Container(
                            content=ft.Text("[Video Placeholder]", size=18, text_align="center"),
                            height=300,
                            bgcolor="lightgray",
                            alignment=ft.alignment.center
                        ),
                        user_input,
                        ft.Container(
                            content=ft.ElevatedButton("Submit", on_click=lambda e: check_answer(word)),
                            alignment=ft.alignment.bottom_right,
                            padding=ft.padding.only(right=20, bottom=20),
                        )
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                )
            )
            page.update()

        # Show the placeholder and word
        content_container.controls.clear()
        content_container.controls.append(
            ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text("[Video Placeholder]", size=18, text_align="center"),
                        height=300,
                        bgcolor="lightgray",
                        alignment=ft.alignment.center
                    ),
                    ft.Text(f"The word is: {word}", size=20, weight="bold"),
                    ft.Container(
                        content=ft.ElevatedButton("Next", on_click=proceed_to_typing),
                        alignment=ft.alignment.bottom_right,
                        padding=ft.padding.only(right=20, bottom=20),
                    )
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        )
        page.update()

    # Function to check the user's answer
    def check_answer(correct_word):
        nonlocal video_index, score
        if user_input.value.strip().lower() == correct_word.lower():
            result_text.value = "Correct! 🎉"
            result_text.color = "green"
            score += 1
        else:
            result_text.value = f"Wrong! The correct word was: {correct_word}"
            result_text.color = "red"

        video_index += 1
        user_input.value = ""  # Clear the input field
        load_video()

    # Function to display the final results
    def display_results():
        router.navigate(f"/results/{score}/{len(video_data)}")
        page.clean()
        user_id = get_current_user()
        add_score(user_id, score, "video_word_game",len(video_data))

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
        icon=ft.icons.PERSON,
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

    # Load the first placeholder
    load_video()

    # Return the view for the router
    return ft.View(
        route="/video_word_game",
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
