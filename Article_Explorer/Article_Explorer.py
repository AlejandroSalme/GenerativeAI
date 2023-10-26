from haystack.nodes import PreProcessor, PromptTemplate, PromptNode, PDFToTextConverter, AnswerParser
from haystack.nodes.prompt.invocation_layer.handlers import TokenStreamingHandler
from haystack.document_stores import InMemoryDocumentStore
import streamlit as st
import tempfile
import openai
import time
import os
import re

class MyCustomTokenStreamingHandler(TokenStreamingHandler):
    """
    Custom handler to allow printing real-time model response in Streamlit.
    """
    def __init__(self, container, initial_text="") -> None:
        self.container = container
        self.text=initial_text
    
    def __call__(self, token_received, **kwargs) -> str:
        self.text += token_received+"/"
        self.container.write(self.text.replace('/', '') + "▌")
        time.sleep(0.05)

        return token_received
    
    def __set_container__(self, container) -> None:
       self.container = container

def is_valid_api_key(openai_api_key):
    """
    Check if the provided key is valid by trying to list OpenAI models.

    Parameters:
        openai_api_key: API Key to be checked
    
    Return:
        True (valid) or False (!valid)
    """
    openai.api_key=openai_api_key
    try:
        openai.Model.list()
    except openai.error.AuthenticationError as e:
        return False
    else:
        return True

def new_chat_message(role: str, message: str, container, store: bool):
    """
    Creates a new chat message for the specified role. 
    Generates a new container or used one created before to write the message.
    Saves chat message in the history chat if indicated.

    Parameters:
        role: user or assistant
        message: message to show
        container: container where to write
        store: save message or not
  
    """
    with st.chat_message(role):
        msg_container = container or st.empty()
        msg_container.write(message)

    if store:
        st.session_state.messages.append({"role": role, "content": message})

def print_chat_history():
    """
    Print past chat messages
    """
    for message in st.session_state.messages:
        new_chat_message(message["role"], message["content"], None, False)


def store_message(role, message):
    """
    Saves chat message in history chat.

    Parameters:
        role: user or assistant
        message: message to store
    """
    st.session_state.messages.append({"role": role, "content": message})

def store_doc(uploaded_file):
    """
    Created a temporary copy of the uploaded file, process it and store the converted file
    in the selected Haystack document sotore.

    Haystack converter needs the file path and at this time do not provide other method
    that allows to read the Streamlit uploaded file directly.

    Parameters:
        uploaded_file: file to be stored
    """
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    converter = PDFToTextConverter(remove_numeric_tables=True)
    doc_text = converter.convert(file_path=temp_path, meta=None)[0]

    doc_processed = st.session_state.preprocessor.process([doc_text])
    st.session_state.document_store.write_documents(doc_processed)


def get_questions(questions):
    """
    Extract questions from the list.

    Parameters:
        questions: pair of question/answer
    """
    qa = re.split(r'(.*\?)', questions)
    qa = [q for q in qa if q]

    q_list = []

    for i in range(0, len(qa), 2):
        question = qa[i]
        q_list.append(question)
    
    return q_list

def generate_output(name, template, prompt_node, past_questions):
    """
    Creates a summary or five questions/answers for the uploaded file.

    Parameters:
        name: summary or questions
        template: prompt to be used
        prompt_node: haystack node
        past_questions: past generated questions
    
    Return 
        response: model output
    """
    with st.spinner('Generating ' + name + '...'):
        with st.chat_message('assistant'):
            st.write(name + ':')
            
            container = st.empty()
            st.session_state.custom_handler.__set_container__(container)  

            response = ''

            if past_questions is None: #Sumary generation
                response = prompt_node.prompt(prompt_template=template,
                                        documents=st.session_state.document_store.get_all_documents())[0].answer
            else: #Question generation
                response = prompt_node.prompt(prompt_template=template,
                                                documents=st.session_state.document_store.get_all_documents(),
                                                past_generated_questions=past_questions)[0].answer
            container.empty()
            container.write(response)

def set_session_components():
    # Default model
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo-16k"

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Uploaded file
    if "last_uploaded_file" not in st.session_state:
        st.session_state.last_uploaded_file = ""

    # Haystack components and prompts
    if "document_store" not in st.session_state:
        st.session_state.document_store = InMemoryDocumentStore(use_bm25=True)

    if "preprocessor" not in st.session_state:
        st.session_state.preprocessor = PreProcessor(
            # Avoid document boundaries fall in the middle of sentences
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=False,
            split_by="word",
            split_length=400,
            split_respect_sentence_boundary=True
        )
    
    if "custom_handler" not in st.session_state:
        st.session_state.custom_handler = MyCustomTokenStreamingHandler(None)

    if "qanswering_template" not in st.session_state:
        st.session_state.qanswering_template = PromptTemplate(
            prompt="""
            Synthesize a comprehensive answer from the following documents for the given question.
            Provide a clear and concise response that summarizes the key points and information presented in the text.
            In case the answer is not in the given text your should respond that the given text does not provide any information about the question.
            Your answer should be appropriate for the length and complexity of the original questions. 
            The output answer should be printed in a new line after the question.
            Documents: {join(documents)} 
            Question: {query} 
            Answer:""",
            output_parser=AnswerParser(),
        )

    if "qgeneration_template" not in st.session_state:
        st.session_state.qgeneration_template = PromptTemplate(
            prompt="""
            Propose five possible questions to ask on the given documents related with their content and the associated answer.
            The generated questions should be different from the past questions made: {', '.join(past_generated_questions)};,
            if this is not possible inform that all posible questions were generated.
            Your generated questions should be no longer than 50 words.
            Documents:{join(documents)};
            Answer:
            """,
            output_parser=AnswerParser(),
        )

    if "summarization_template" not in st.session_state:
        st.session_state.summarization_template = PromptTemplate(
            prompt="""
            Provide a comprehensive summary of the given document, covering the most important key points in an easy-to-understand way.
            The summary should include an small explanation of the selected main key points. Avoiding information repetition and also they way the concepts are explained. 
            The length of the summary should be appropriate for the length and complexity of the original document.
            Documents:{join(documents)};
            Answer:
            """,
            output_parser=AnswerParser(),
        )

def main():
    # Page title
    st.set_page_config(page_title='Article exploration App')
    st.title('Article exploration App')

    # File upload and OpenAI API key
    with st.sidebar:
        uploaded_file = st.file_uploader("Select an article: ", type=['pdf'])
        openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
        
        "[View the source code](https://github.com/AlejandroSalme/GenerativeAI/blob/master/Article_Explorer/Article_Explorer.py)"

    set_session_components()

    print_chat_history()
    
    if uploaded_file:
        is_new_file = st.session_state.last_uploaded_file != uploaded_file.name

        if is_new_file:
            new_chat_message('assistant', 'File processed', None, False)
            
            store_doc(uploaded_file)

            st.session_state.last_uploaded_file = uploaded_file.name
            st.session_state.summary = ''
            st.session_state.questions = []
        
        if is_valid_api_key(openai_api_key):
            
            prompt_node = PromptNode(
                model_name_or_path=st.session_state.openai_model, 
                api_key=openai_api_key, 
                max_length=512,
                model_kwargs={"stream_handler": st.session_state.custom_handler}
            )       

            is_summary_generated = st.session_state.summary != ''
            is_questions_generated = len(st.session_state.questions) != 0

            if not is_summary_generated:
                #Summary
                summary = generate_output('Summary', st.session_state.summarization_template, prompt_node, None)

                store_message('assistant', 'Summary:\n\n\n' + summary)
                st.session_state.summary = summary

            if  not is_questions_generated:
                #Questions
                questions = generate_output('Questions', st.session_state.qgeneration_template, st.session_state.questions)
            
                question_list = get_questions(questions)
                store_message('assistant', 'Questions:\n\n\n' + questions)
                st.session_state.questions.append(question_list)
                print(question_list)
        
            # User input
            if prompt := st.chat_input("Ask me something"):

                new_chat_message('user', prompt, None, True)

                with st.chat_message('assistant'):
                    # Assistant response
                    message_placeholder = st.empty()
                    st.session_state.custom_handler.__set_container__(message_placeholder)

                    response = prompt_node.prompt(prompt_template=st.session_state.qanswering_template, 
                                                  query=prompt, 
                                                  documents=st.session_state.document_store.get_all_documents())[0].answer
                    store_message('assistant', response)

        elif openai_api_key != '':
            new_chat_message('assistant', 'OpenAI API Key is not valid', None, False)

    else:
        new_chat_message('assistant', 'Start by choosing a file and introduce a valid openAI API Key', None, False)

if __name__ == "__main__":
    main()