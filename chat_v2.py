import openai
import streamlit as st
import time

assistant_id = "asst_7vzuqPzzsJf8JULzJC00EZBs"

client = openai

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(page_title="BiaBa.AI [Powered by Cantrak]", page_icon=":speech_balloon:")


# Hide the sidebar menu
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("BiaBa.AI")
st.write("I am a customer-focused Cannabis Specialist, knowledgeable in strains and consumption methods. Here to assist and recommend tailored products. [Powered by Cantrak]")

# Place "Start Chat" button below the introductory text
if st.button("Start Chat"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if st.button("Clear Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-1106-preview"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Try: I need something to help me relax..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Display loading spinner while waiting for the response
        with st.spinner("BiaBa.AI is thinking..."):
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                instructions="As a customer-focused and knowledgeable Budtender - Cannabis Specialist Chatbot, you possess an in-depth understanding of various strains, consumption methods, and product attributes. You will leverage internal files to adeptly respond to customer queries and recommend suitable cannabis products. When responding, make sure to respond with only 1 single product and keep the response within 1 sentence. Also prices are in Thai Baht. For dried flower, it is price per gram. Lastly don't show source"
            )

            while run.status != 'completed':
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )

            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                st.session_state.messages.append(
                    {"role": "assistant", "content": message.content[0].text.value})
                with st.chat_message("assistant"):
                    st.markdown(message.content[0].text.value)

else:
    st.write("Click 'Start Chat' to begin.")
