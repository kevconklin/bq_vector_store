from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict
import os

from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_community import BigQueryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_google_vertexai import VertexAI
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate


app = FastAPI()

PROJECT_ID = os.getenv('PROJECT_ID')
REGION = os.getenv('REGION')
DATASET = os.getenv('DATASET')
TABLE = os.getenv('TABLE')

# create embedding and llm model objects
embedding = VertexAIEmbeddings(
    model_name="textembedding-gecko@latest", project=PROJECT_ID)
llm = VertexAI(model_name="gemini-1.5-flash-002")

# bigquery as a vector store
store = BigQueryVectorStore(
    project_id=PROJECT_ID,
    dataset_name=DATASET,
    table_name=TABLE,
    location=REGION,
    embedding=embedding,
)

retriever = store.as_retriever(
    search_kwargs={
        "k": 10
    }
)

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know."
    "\n\n"
    "{context}"
)

contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# empty chat history
chat_history = []

# create rag chain
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

@app.post("/upload_pdf")
async def upload_pdf(request: Request):
    """ 
    Function that uploads a pdf to a BigQuery vector store
    Input must be a url.

    Args:
        request (Request): the post request from client. Must
        contain json data with 'pdf_url' key.


    Returns:
        (dict): successful message
    """
    
    # get data from request
    json_data = await request.json()
    pdf_url = json_data['pdf_url']
    
    loader = PDFPlumberLoader(pdf_url)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200)
    
    splits = text_splitter.split_documents(docs)

    store.add_documents(splits)

    return {"message": "PDF uploaded successfully"}

@app.post("/ask_question")
async def ask_question(request: Request):
    """
    Allows a question to be asked to the chains defined above.

    Args:
        request (Request): the post request from client. Must
        contain json data with 'question' key.

    Returns:
        answer (str): The answer to the user's question
    """
    # get data from request
    json_data = await request.json()
    question = json_data['question']
    
    # invoke rag chain
    response = rag_chain.invoke(
        {
            "input": question,
            "chat_history": chat_history
        }
    )
    
    answer = response["answer"]
    
    # extend in memory chat store
    chat_history.extend(
        [
            HumanMessage(content=question),
            AIMessage(content=answer),
        ]
    )
    
    return answer
