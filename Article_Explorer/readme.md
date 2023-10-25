## Article exploration App (Streamlit + Haystack) [[code]]() 

![image title](https://img.shields.io/badge/Python-3.9-purple.svg) ![Image title](https://img.shields.io/badge/Haystack-1.22.0-green.svg) ![Image title](https://img.shields.io/badge/Streamlit-1.27.2-red.svg) ![Image title](https://img.shields.io/badge/OpenAI-0.28.1-blue.svg)

## Overview
This project leverages OpenAI's powerful LLMs (gpt-3.5) in conjunction with the Streamlit and Haystack to create an interactive document exploration system. We use Haystack as an alternative LLM framework to LangChain.

The system allows users to input an article and retrieve a summary, along with a set of suggested questions and their corresponding answers. Additionally, users can interactively ask their own questions about the document and receive immediate answers. 

This type of systems offers significant advantages:
- User-friendly interface
- Efficient summarization
- Facilitates inquiry
- Instantaneous responses

So in summary the system empowers users to efficiently navigate, comprehend, and interact with textual content. It enhances learning, research, and information retrieval processes, making it a valuable tool in a variety of domains.

## Usage

Streamlit:
1. Load an [article](https://arxiv.org/pdf/1706.03762.pdf).
2. Insert a valid [OpenAI API Key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key).
3. The app will automatically generate a summary and five questions that could be made to the document, and their corresponding answer.
4. A message bar will appear allowing user make questions about the document.



Local:
1. git clone repo
2. cd document-exploration-system-path
3. streamlit run Article_Explorer.py
4. Follow the above Streamlit usage instructions

## Requirements

- OpenAI API Key
- haystack
- streamlit
- openai

## Future ideas
- Add a button to generate new questions automatically, preventing them from being similar to the previous ones already stored.