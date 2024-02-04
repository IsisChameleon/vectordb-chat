# Chat about Vector DB with Streamlit, OpenAI, and GripTape

This repository contains a simple chatbot built with Streamlit, OpenAI, and GripTape agent that can answer questions about a selection of vector databases


### Key Features

- **Streamlit:** A powerful, fast Python framework used to create the web interface for the chatbot.
- **OpenAI's GPT:** A state-of-the-art language processing AI model that generates the chatbot's responses.
- **LangChain:** A wrapper library for the ChatGPT model that helps manage conversation history and structure the model's responses.

## Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vectordb-chat.streamlit.app/)

## How to Run

### Prerequisites

- Python 3.6 or higher
- Streamlit
- griptape
- OpenAI API key

### Steps

1. Clone this repository.
2. Install the necessary Python packages using the command `pip install -r requirements.txt`.
3. Set the environment variable for your OpenAI API key.
4. Run the Streamlit app using the command `streamlit run app_st.py`.

## TO DO

1. User message disappears while waiting for answers from agent. Should be displayed earlier.
2. Add streaming
3. Log user queries and answers to create a knowledge base (with some LLM monitoring tool)
4. Improve context and speed, maybe save some data in an index (not just real time search etc... agent is slow)


## Contribution

Contributions, issues, and feature requests are welcome. Feel free to check the [Issues](https://github.com/IsisChameleon/vectordb-chat/issues) page if you want to contribute.

## License

This project is licensed under the terms of the MIT license.
