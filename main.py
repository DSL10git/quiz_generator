"""
1. Write python program that can automatically extract transcripts from youtube links
2. Create quizes based on the transcript and create an html version
3. Save the chatgpt response into an html file
"""
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import gradio as gr
import re
import json
import openai


with open("keys.json") as f:
    keys = json.load(f)
def feedback(feedback):
    if feedback == "Y" or feedback == "y" or feedback == "Yes" or feedback == "yes" or feedback == "lovin'it!":
        return "Thank you for your feedback, click flag as like!"
    elif feedback == "N" or feedback == "n" or feedback == "No" or feedback == "no" or feedback == "I HATE IT":
        return "Thank you for your feedback, click flag as dislike!"
    else:
        return "Please enter Y or Yes or N or No or lovin'it or I HATE IT"
def quiz_choice_func(a):
    b = ""
    if a == "Multiple format":
        b = "Include different format of quizes, multi-choice, true/false, type your answer, etc. (If there's more)"
    if a == "Multiple choice":
        b = "Include muti choice, ex. A. 34, B. 24, C. 26, D. none of the above(All should be Multiple choice)"
    if a == "True or False":
        b = "Include True or False questions, ex. True, Falsem(All should be True or False)"
    else:
        b = "type answer, ex. what is the fastest animal in the planet, Type answer _____   (All should be type your answer)"
    return a


def quiz_func(youtube_video_transcript, num_quiz, formats, users_state):
    # Check login
    if not users_state:
        return "Error: User state is not initialized. Please log in first!"
    logged_users = users_state.get('logged_users', set())
    if len(logged_users) == 0:
        return "No users, please log in first!"

    quiz_choice = quiz_choice_func(formats)
    messages = [{"role": "system", "content": "you are chatgpt"}]
    openai.api_key = keys["openai_key"]
    messages.append(
        {
            "role": "user",
            "content":
f"""
Can you create a quiz in html format for this transcript: {youtube_video_transcript}

Requirements:
Include different format of quizes, multi-choice, true/false, etc.
Give {num_quiz} questions in total
After users submitting the answer, the html should show their scores
Return the code directly. Do not include any explanation, comments, or additional text.
""",
        }
    )
    response = openai.ChatCompletion.create(
        model = "gpt-4o-mini",
        messages = messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    lines = ChatGPT_reply.split("\n")
    lines = lines[1:-1]
    ChatGPT_reply = "\n".join(lines)

    print(ChatGPT_reply)

    return gr.update(value=ChatGPT_reply)

def login(username, password, users_state):
    users = users_state['users']
    logged_users = users_state['logged_users']

    if username in users:
        if password == users[username]:
            logged_users.add(username)
            message = "user logged in successfully"
        else:
            message = "password doesn't match"
    else:
        message = "user isn't in the system"

    gr.Info(message)
    return users_state

def extract_video_id(youtube_url):
    """Extract the video ID from a YouTube URL."""
    video_id_match = re.search(r'v=([\w-]+)', youtube_url)
    if video_id_match:
        return video_id_match.group(1)
    else:
        raise ValueError("Invalid YouTube URL. Please provide a valid link.")

demo_css = """
.gradio-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100vh;
    padding-top: 20px;
}
.recommendation-container {
    display: flex;
    align-items: center;
    margin-top: 10px;
}
.recommendation-image {
    width: 80px;
    height: 80px;
    border-radius: 10px;
    margin-left: 10px;
"""
with gr.Blocks(css=demo_css) as demo:
    with gr.Row():
        about_btn = gr.Button("About", scale=0)
        title = gr.HTML("""
            <h1 style="text-align:center"> Quiz generator By Daniel</h1>
        """)
    url_txt_box = gr.Textbox(
        label="Enter a URL:",
        value="https://www.youtube.com/watch?v=aY0YrwHlwhM",
    )
    format_unit = gr.Radio(
        ["Multiple format", "Multiple choice", "True or False", "Type your answer"],
        label="Format", info="Example: Multiple format(all three combined), Multiple choice, True or False, and Type your answer",
        value="Multiple format"
    )
    num_of_questions = gr.Textbox(
        label="Enter a number of questions(Do not go over 20 questions): ",
        value=10,
    )
    submit = gr.Button("Submit")
    username_txt = gr.Textbox(label="Username", type="text")
    password_txt = gr.Textbox(label="Password", type="password")
    login_btn = gr.Button("Login")
    code = gr.HTML("""""")
    users_state = gr.State({
        "users": keys["users"],
        "logged_users": set()
    })
    login_btn.click(
        login,
        inputs=[username_txt, password_txt, users_state],
        outputs=[users_state]
    )
    submit.click(
        quiz_func,
        inputs=[
            url_txt_box,
            num_of_questions,
            format_unit,
            users_state
        ],
        outputs=[code]
    )
    flagging = gr.Interface(
        fn=feedback,
        inputs="text",  # Hidden input to satisfy Gradio's requirement
        outputs="text",  # Hidden output to satisfy Gradio's requirement
        live=False,  # Prevents triggering unnecessary updates
        flagging_options=["like", "dislike"]  # Only flagging options
    )
demo.launch(server_name="0.0.0.0", server_port=7861, share=False)
