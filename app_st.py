# Import required libraries
from dotenv import load_dotenv
from itertools import zip_longest
import os

import streamlit as st
from streamlit_chat import message

# Create a Griptape Agent and give it a WebScraper tool
# Use the Chat utility to chat with it.

from griptape.structures import Agent
from griptape.tools import WebScraper
from griptape.utils import Chat
from griptape.engines import VectorQueryEngine
from griptape.loaders import WebLoader
from griptape.rules import Ruleset, Rule
from griptape.structures import Agent
from griptape.tools import VectorStoreClient, BaseTool
from griptape.utils import Chat
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver

from sidebar_st import Sidebar


# Load environment variables
load_dotenv()

# Set streamlit page configuration
st.set_page_config(layout="wide", page_title="Chat about Vector Dbs")
st.title("Chat about Vector Dbs")

# Instantiate the main components
sidebar = Sidebar()

# Initialize session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []  # Store AI generated responses

if 'past' not in st.session_state:
    st.session_state['past'] = []  # Store past user inputs

if 'entered_prompt' not in st.session_state:
    st.session_state['entered_prompt'] = ""  # Store the latest user input

# Initialize agent


# def build_message_list():
#     """
#     Build a list of messages including system, human and AI messages.
#     """
#     # Start zipped_messages with the SystemMessage
#     zipped_messages = [SystemMessage(
#         content="You are a helpful AI assistant talking with a human. If you do not know an answer, just say 'I don't know', do not make up an answer.")]

#     # Zip together the past and generated messages
#     for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
#         if human_msg is not None:
#             zipped_messages.append(HumanMessage(
#                 content=human_msg))  # Add user messages
#         if ai_msg is not None:
#             zipped_messages.append(
#                 AIMessage(content=ai_msg))  # Add AI messages

#     return zipped_messages
def load_api_key():
    """
    Loads the OpenAI API key
    """
    user_api_key = st.sidebar.text_input(
        label="#### Your OpenAI API key 👇", placeholder="sk-...", type="password"
    )
    if user_api_key:
        st.sidebar.success("API key loaded from sidebar", icon="🚀")
        return user_api_key

    load_dotenv(override=True)
    if os.getenv("OPENAI_API_KEY") != "":
        st.sidebar.success("API key loaded from .env", icon="🚀")

    return os.getenv("OPENAI_API_KEY")

def generate_response(agent:Agent, user_query: str):
    """
    Generate AI response using the ChatOpenAI model.
    """
    # Build the list of messages to provide context

    # add to prompt

    response = agent.run(user_query)

    # Generate response using the chat model
    ai_response = response.output_task.output.to_text()
    print('____________________AI_RESPONSE__________________')
    print(ai_response)

    return ai_response

def show_api_key_missing():
        """
        Displays a message if the user has not entered an API key
        """
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Enter your <a href="https://platform.openai.com/account/api-keys" target="_blank">OpenAI API key</a> to start chatting</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
# Define function to submit user input
def submit():
    # Set entered_prompt to the current value of prompt_input
    st.session_state.entered_prompt = st.session_state.prompt_input
    # Clear prompt_input
    st.session_state.prompt_input = ""

def api_key_present():
    user_api_key = load_api_key()
    if not user_api_key:
        show_api_key_missing()
        return False
    else:
        os.environ["OPENAI_API_KEY"] = user_api_key
        return True

def configure_vector_tool(namespace: str, url: str, url_description: str):

    engine = VectorQueryEngine(
        vector_store_driver=LocalVectorStoreDriver(
            embedding_driver=OpenAiEmbeddingDriver(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        )
    )

    artifacts = WebLoader().load(url=url)

    engine.vector_store_driver.upsert_text_artifacts(
        {namespace: artifacts}
    )

    vector_store_tool = VectorStoreClient(
        description=f"Contains information about {url_description}",
        query_engine=engine,
        namespace=namespace,
        off_prompt=False
    )

    return vector_store_tool

def configure_agent(tools: list[BaseTool]):
    agent = Agent(
        rulesets=[
            Ruleset(
                name="Vector Database Expert",
                rules=[
                    Rule(
                        "Be truthful. Be specific. Only use information extracted from your tools. Provide citation or url for your statements."
                    )
                ]
            )
        ],
        tools=tools
        )
    return agent


def submit_first_description_query(agent:Agent, url_description: str):

    first_query = """
        For {url_description}, provide a paragraph of text that highlights the characteristics of this vector database. 
        Look in the main page of the website for a tagline and provide a summary of the features."""
    
    user_query = first_query.format(url_description=url_description)

            # Generate response
    output = generate_response(agent, user_query)

    # Append AI response to generated responses
    return output

def st_exists(name: str):
    return name in st.session_state and name != ""

def main_processing():
    if not api_key_present():
        return
    
    # Select Vector Database to chat about
    sidebar.url_selector()
    if st.session_state["selected_url"] == "":
        st.write("Please select a URL to chat about...")
        return
    
    # Configure vector engine
    namespace = st.session_state["selected_description"]
    if st.session_state["url_changed"]:
        url = st.session_state["selected_url"]
        url_description = st.session_state["selected_description"]
        st.session_state.vector_tool = configure_vector_tool(namespace, url, url_description)

        st.session_state.agent = configure_agent([st.session_state.vector_tool])

        intro_text = submit_first_description_query(st.session_state.agent, url_description)
        print(intro_text)
        st.session_state["intro_text"] = intro_text


    if st_exists("intro_text"):
        st.markdown(f'<div style="border:1px solid #ddd; border-radius: 5px; padding: 10px; margin: 10px 0;">{st.session_state["intro_text"]}</div>', unsafe_allow_html=True)
    
    # Show sidebard

    # Create a text input for user
    st.text_input('YOU: ', key='prompt_input', on_change=submit)


    if st.session_state.entered_prompt != "":
        # Get user query
        user_query = st.session_state.entered_prompt

        # Append user query to past queries
        st.session_state.past.append(user_query)

        # Generate response
        output = generate_response(st.session_state["agent"], user_query)

        # Append AI response to generated responses
        st.session_state.generated.append(output)

    # Display the chat history
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            # Display AI response
            message(st.session_state["generated"][i], key=str(i))
            # Display user message
            message(st.session_state['past'][i],
                    is_user=True, key=str(i) + '_user')

main_processing()

# Add credit
st.markdown("""
---
lala isabelle""")
