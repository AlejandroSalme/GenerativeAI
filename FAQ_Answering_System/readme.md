## Frequently Asked Questions (FAQ) Answering System [[code]](https://github.com/AlejandroSalme/GenerativeAI/blob/master/FAQ_Answering_System/FAQ_Answering_System.ipynb) 

![image title](https://img.shields.io/badge/Python-3.9-purple.svg) ![Image title](https://img.shields.io/badge/Haystack-1.22.0-green.svg) ![Image title](https://img.shields.io/badge/BeautifulSoup-4.12.2-blue.svg) ![Image title](https://img.shields.io/badge/Pandas-2.1.1-red.svg)  

## Overview
This project aims to build a first aproach of a Frequently Asked Questions (FAQ) answering system using both generative and non-generative models. The system is implmented in Python, using Hugging Face and openAI models, and Haystack for scalable, efficient information retrieval and natural language generation.

## Features

- Non-generative QA system: Based on a similarity model, it finds the most similar stored question to the one asked by the user, and outputs the answer associated with it.

- Non-generative QA + Text-to-Speech (TTS) system: Similar to the first aproach transforming the output answer into speech.

- Generative QA + RAG (Retrieval-Augmentation) system: Utilizes a pre-trained language model (davinci-003) and retrieval augmented generation (RAG) approach, to answer user queries, conditioning the answer to our documents info.