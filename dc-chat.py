import openai
import os
import streamlit as st
from PIL import Image
import tiktoken


st.set_page_config(
    page_title="Customer Service - (Delivery Service)",
    page_icon="🧑‍⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

hide_menu_style = """
<style>
#MainMenu {visibility: hidden;}
</style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

image = Image.open("delivery-banner.jpg")
st.image(image)

st.subheader("🧑‍⚕️:blue[Customer Service - Delivery Department]")
st.markdown('##### Good Morning! We will arrange your delivery order, please enter your inquiry.')


log = ''

with st.sidebar:
    st.markdown("""This program will demo how the rotbot collect infotmraion for delivery notes.  
            ie : (Name, Address, Telephone number, Available delivery time), and prepare the final statement for conformation.  
            To simplify the program, validation has not implemented. see the sample screens on sidebar for action.
            """
            )
    system_openai_api_key = os.environ.get('OPENAI_API_KEY')
    system_openai_api_key = st.text_input(":key: OpenAI Key :", value=system_openai_api_key)
    os.environ["OPENAI_API_KEY"] = system_openai_api_key
    
    




def cal_cost(texts):
    enc = tiktoken.encoding_for_model(st.session_state["openai_model"])
    total_tokens = len(enc.encode(texts))
    costing = f'Tokens: {str(total_tokens)} , USD: str({total_tokens / 1000 * 0.0004:.6f})'
    st.sidebar.write(costing)


 

def addLog(in_log):
    global log  
    #  st.sidebar.write(in_log)
    log = '\n' + log + in_log

# store in session variables
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"
    
    # st.session_state["openai_model"] = "text-embedding-ada-002"
    
    addLog(f'Model: {st.session_state["openai_model"]}')

# create message [] when the app is first created
if "messages" not in st.session_state:
    st.session_state.messages = []
    addLog('Initializing session store and messages[]')

# loop each message from messages[]
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    # creates a chat bubble for the message's role 
    with st.chat_message(message["role"]):
        # displays the message.
        st.markdown(message["content"])

system_prompt = """
OpenAI will ask the following questions:
1. Name
2. Address
3. Telephone number
4. Available delivery time

OpenAI will keep asking until all answers are collected and the delivery statement is completed.

Guideline:
- If the user asks unrelated questions, the chatbot will ask for delivery information.
- Correct answers will be stored in variables: {username}, {address}, {telno}, {deliverytime}.
- Validation rules:
  1. Name: String, 1-20 characters.
  2. Address: Alphanumeric, 1-100 characters.
  3. Telephone number: 9-digit string with '-', '(', and ')'.
  4. Delivery time: Alphanumeric, 1-20 characters.

Delivery statement will be created as:
Dear {username},
Thank you for your order! We will deliver to {address} at {deliverytime}. Our staff will call/WhatsApp you at {telno} 2 hours before.
Reply 'Yes' to confirm or keep asking for confirmation.
"""

st.session_state.messages.append({"role": "system", "content": system_prompt})
addLog('Add System prompt to message')

# displays the chat input field , use := to assign the value
if prompt := st.chat_input("I want to check my delivery ?"):
    try:
        #  appended to user's entered prompt in dictionary format
        #  to messages[] list with the role "user" 
        st.session_state.messages.append({"role": "user", "content": prompt})
        # display the user message
        with st.chat_message("user"):
            st.markdown(prompt)
        addLog('1. user input message ')

        # Get the current conversation history as a single text string.
        conversation_text = "\n".join(message["content"] for message in st.session_state.messages)

        cal_cost(conversation_text)
        addLog('2. Cal cost')
         



        # prepares to display the assistant's response 
        # assistance = OpenAI 
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # For Loop  ---  iterates over the responses received from the OpenAI API.
            # handle the real-time streaming of partial responses from the OpenAI.
            # openai.ChatCompletion.create() supports Streaming responses in real time sync./ non-blocking responses
            addLog('3. send to GPT by ChatModel')
            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                # messages is is a list of dictionaries =  conversation messages
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True, # enabling the real-time streaming of responses.
            ):
                # the final assistant's response is displayed without the "+▌" formatting to indicate that the response is complete.
                # combine all parital response 
                full_response += response.choices[0].delta.get("content", "")
                addLog('4. receiving reply ... ')
                #  display whole message 
                # "+▌"  indicate that it is a partial response 
                message_placeholder.markdown(full_response + "▌")
                

            # indicate that the response is complete.
            message_placeholder.markdown(full_response)
            addLog('5. display whole message ')

        #  complete response is appended to the messages
        #  conversation history is updated with the assistant's response for future iterations 
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        addLog('5. add assistant full message on message history')
    except Exception as e:
        error_message = "Oops! Something went wrong. Please try again later."
        with st.chat_message("assistant"):
            st.markdown(error_message)
        addLog(f"Error: {e}")



with st.sidebar:
    with st.expander("Log"):
        st.code(log)

    with st.expander("sample screen"):
        image = Image.open("delivery-notes-sample-1.jpg")
        st.image(image)

        image = Image.open("delivery-notes-sample-2.jpg")
        st.image(image)

    with st.expander("Funny example"):
        image = Image.open("delivery-notes-sample-3.jpg")
        st.image(image)

        image = Image.open("delivery-notes-sample-4.jpg")
        st.image(image)
