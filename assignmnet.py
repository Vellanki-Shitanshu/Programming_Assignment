import streamlit as st
import os
import json
from dotenv import load_dotenv
from openaipackage import OpenAIEngine  # Make sure this module is defined with the required methods
import datetime

# Load environment variables
load_dotenv()

# Initialize the OpenAI engine
engine = OpenAIEngine()

# Streamlit app title
st.title("OpenAI API")

# Initialize session state variables if not already initialized
if "memory" not in st.session_state:
    st.session_state["memory"] = []

if "image_folder" not in st.session_state:
    st.session_state["image_folder"] = "saved_images"

# Define options for the dropdown lists
chat_model_list = ["gpt-3.5-turbo", "gpt-4-turbo-preview", "gpt-4-vision-preview"]
image_model_list = ["dall-e-3", "dall-e-2"]
chat_prompt_dictionary = {
    "Code Assistant": """You are a code assistant. 
    Answer questions in code with minimal to no explanation.
    Put brief one line comments on the code for explanation.""",
    "General Assistant": """You are a general AI assistant. 
    Answer questions with minimal and to-the-point explanations.
    Only warn about security, without cultural or safety disclaimers."""
}

# Sidebar for selecting options
st.session_state["app_type_option"] = st.sidebar.selectbox("Generation Type:", ["Chatting", "Image Generation"])
st.sidebar.write(f'You are in {st.session_state.app_type_option} mode.')

# List of models changes based on the type of generation
model_list = chat_model_list if st.session_state.app_type_option == "Chatting" else image_model_list

# Dropdown for model selection
st.session_state["selected_option_1"] = st.sidebar.selectbox('Models:', model_list)

# Dropdown for selecting prompt type if in Chatting mode
if st.session_state.app_type_option == "Chatting":
    st.session_state.selected_option_2 = st.sidebar.selectbox('Prompts:', chat_prompt_dictionary.keys())
    st.sidebar.write(f'You are using "{st.session_state.selected_option_1}" together with "{st.session_state.selected_option_2}" prompt.')
else:
    st.sidebar.write(f'You are using "{st.session_state.selected_option_1}".')

# Define OpenAI engine configuration
engine.change(
    st.session_state.app_type_option,
    st.session_state.selected_option_1,
    chat_prompt_dictionary.get(st.session_state.selected_option_2, "")
)

# Update the chat page with messages from memory
for message in st.session_state["memory"]:
    if message["role"] == "image assistant":
        with st.chat_message("assistant"):
            st.image(message["content"])
    elif message["role"] == "system":
        pass
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Entering new message event handle
if prompt := st.chat_input("Start chat ..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if st.session_state.app_type_option == "Chatting":
            response = engine.generate_answer(prompt)
            st.markdown(response)
            # Save to memory
            st.session_state["memory"].append({"role": "assistant", "content": response})
        else:
            image = engine.generate_image(prompt)
            st.image(image)
            # Save image path to memory
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            image_path = os.path.join(st.session_state["image_folder"], f"image_{timestamp}.png")
            image.save(image_path)
            st.session_state["memory"].append({"role": "image assistant", "content": image_path})

# Load image history on app start
history_file = os.path.join(st.session_state["image_folder"], "image_history.json")
if os.path.exists(history_file):
    with open(history_file, "r") as f:
        history_data = json.load(f)
        for item in history_data:
            st.session_state["memory"].append({"role": "image assistant", "content": item["path"]})

# Save new image paths to the history file
def update_image_history(image_path):
    os.makedirs(st.session_state["image_folder"], exist_ok=True)
    history_data = []

    # Load existing history if available
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history_data = json.load(f)
    
    # Append new image entry
    history_data.append({"path": image_path, "timestamp": datetime.datetime.now().isoformat()})
    
    # Write updated history back to the file
    with open(history_file, "w") as f:
        json.dump(history_data, f)
