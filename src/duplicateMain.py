from fastapi import FastAPI, File, Form, UploadFile, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_community.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse, FileResponse
import os
import traceback
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pinecone import Pinecone
import numpy as np
from openai import AsyncOpenAI
from typing import Dict, List, Optional
import aiofiles
from fastapi import FastAPI, File, Form, UploadFile, Depends, HTTPException, Request
import json
from data_loader import load_documents
from upload import upload_data
import logging
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
import os
import aiofiles
import logging
import traceback
import json
from typing import List
from dotenv import load_dotenv
from data_loader import load_documents
from upload import upload_data
from agents import (scrapeFromLocation, AgenticScrap, 
                    get_coordinates,create_map,extract_dictionaries_from_file,
                    extract_dictionaries,save_dictionaries_to_json,extract_addresses_from_json)
from fastapi.responses import HTMLResponse
# import pinecone

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_API_TYPE = os.getenv("AZURE_OPENAI_API_TYPE")
OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
HF_INFERENCE_API_KEY = os.getenv("HF_INFERENCE_API_KEY")
GEOLOCATION_API= os.getenv("GEOLOCATION_API")

# Initialize FastAPI
app = FastAPI()

# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LangChain AzureChatOpenAI model
llmGetDisease = AzureChatOpenAI(
    openai_api_version=OPENAI_API_VERSION,
    openai_api_key=OPENAI_API_KEY,
    openai_api_base=OPENAI_API_BASE,
    openai_api_type=OPENAI_API_TYPE,
    deployment_name="shecodes", ## For getting diseases
    temperature=0.7
)

llmGetResponse = AzureChatOpenAI(
    openai_api_version=OPENAI_API_VERSION,
    openai_api_key=OPENAI_API_KEY,
    openai_api_base=OPENAI_API_BASE,
    openai_api_type=OPENAI_API_TYPE,
    deployment_name="GetResponse",
    temperature=0.7
)

# Initialize Pinecone
pc=Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(name=PINECONE_INDEX_NAME)

logging.info(index.describe_index_stats())

# Function to embed text using HuggingFace API
def embed_text(texts):
    API_URL = "https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5"
    embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key=HF_INFERENCE_API_KEY, model_name="BAAI/bge-large-en-v1.5", api_url=API_URL
    )
    if isinstance(texts, str):
        texts = [texts]
    embedding = embeddings.embed_documents(texts)
    return embedding

logging.info("Vector store successfully initialized with Pinecone and LangChain.")

namespace = 'default'

class Query(BaseModel):
    query: str

class Namespace(BaseModel):
    set_namespace: str

class User(BaseModel):
    lat: float
    long: float    

class DoctorRequest(BaseModel):
    specialization: str
    location: str
    user: User

@app.post("/set_namespace")
async def set_namespace(setNamespace: Namespace):
    global namespace
    namespace = setNamespace.set_namespace
    logging.info(f"Namespace set to {namespace}")
    return {"message": "Namespace set successfully", "namespace": namespace}

@app.post("/upload/files")
async def upload_files(
    files: List[UploadFile],
    metadata: str = Form(...),
):
    total_docs = []
    save_dir = "datasets"
    os.makedirs(save_dir, exist_ok=True)

    for file in files:
        file_path = os.path.join(save_dir, file.filename)
        content = await file.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        await file.close()

        if not isinstance(metadata, dict):
            metadata = json.loads(metadata)

        docs = load_documents(
            file_name=file.filename,
            file_path=file_path,
            chunk_size=1000,
            metadata_obj=metadata,
        )
        total_docs.extend(docs)
    try:
        upload_data(total_docs, namespace)
        return {"message": "Files uploaded successfully", "metadata": metadata}, 200
    except Exception as e:
        traceback.print_exc()
        logging.error(f"Error uploading files,\n {traceback.format_exc()}")
        raise e

@app.post("/get_disease")
async def get_disease():
    try:
        query = "List all the diseases and problems that the patient is suffering from"
        logging.info(f"Received query: {query}")
        query_values = embed_text(query)
        query_response = index.query(
            top_k=50,
            vector=query_values,
            include_values=True,
            include_metadata=True,
            namespace=namespace,
        )

        context = ""
        for match in query_response["matches"]:
            context += match["metadata"]["text"] + "\n"

        max_tokens = 3000
        context_tokens = context.split()
        if len(context_tokens) > max_tokens:
            context = ' '.join(context_tokens[:max_tokens])

        logging.info(f"Constructed context: {context}")

        prompt_template = """
        Context: {context}
        Question: {question}

        Based on the context provided, list all the diseases and problems that the patient is suffering from. 
        Do not include diseases or problems that are explicitly stated as negative or absent. 
        Things to return:
        1. If there is nothing inside the context: {context} , or no relevant disease names which is mentioned to be a problem/disease suffered by the patient inside it then return an empty list like this -> [] , and don't give any other answer except the list i.e. []  .
        2. If not empty, then return the list of diseases and problems in square brackets like this -> [disease1, disease2, disease3] and don't give any other thing inside or outside the answer except the disease names which is mentioned that the patient is suffering from it, else you will get fired from your role.
        
        """
        prompt = prompt_template.format(context=context, question=query)

        prediction = llmGetDisease.predict(prompt)

        logging.info(f"Generated answer: {prediction}")

        response_data = {"answer": prediction}
        return JSONResponse(response_data)
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return JSONResponse(content={"error": str(e)})

@app.post("/get_response")
async def get_response(user_query: Query):
    try:
        query = user_query.query
        logging.info(f"Received query: {query} and index name as {index}")
        query_values = embed_text(query)
        query_response = index.query(
            top_k=10,
            vector=query_values,
            include_values=True,
            include_metadata=True,
            namespace=namespace,
        )

        context = ""
        for match in query_response["matches"]:
            context += match["metadata"]["text"] + "\n"

        max_tokens = 3800
        context_tokens = context.split()
        if len(context_tokens) > max_tokens:
            context = ' '.join(context_tokens[:max_tokens])

        logging.info(f"Constructed context: {context}")
        
        prompt_template = """
        You are a highly knowledgeable and specialized medical professional with expertise in interpreting and analyzing medical reports. Your task is to provide precise, detailed, and helpful answers based on the provided medical context. Ensure your responses are strictly confined to the medical information contained in the context and avoid any general or unrelated information. Your answers should be detailed, relevant to the user's query, and easy for amateurs to understand, explaining medical terms and concepts where necessary.

        Context: {context}

        Question: {question}

        Guidelines:
        1. If the context retrieved has no relevant information to the medical/healthcare domain, then strictly answer that there is no relevant information in the file uploaded to healthcare reports or medical data.
        2. Carefully consider the medical context provided and ensure your answer is directly derived from this context.
        3. If the context mentions multiple conditions but clarifies some as negative, it means clearly that the patient isn't suffering from that disease but it was being tested and the patient doesn't have that disease.
        4. Provide detailed medical advice or information relevant to the question, ensuring it aligns with the medical data in the context.
        5. Explain medical terms and concepts in a way that is easy for amateurs to understand.
        6. Provide detailed answers that are comprehensive and educational when asked by query.
        7. Do not provide answers outside the medical domain or unrelated to the context.
        8. If asked a question regarding any other domain like general knowledge, technical knowledge in software domains, etc., then answer that you are specialized in the medical domain and can't provide answers outside the medical domain.
        9. If you don't know the answer or if the question is from any other domains excluding medical/healthcare, just say that you are not specialized in that domain and thus don't know the answers, don't try to make up an answer.

        Answer:
        """
        prompt = prompt_template.format(context=context, question=query)

        prediction = llmGetResponse.predict(prompt)

        logging.info(f"Generated answer: {prediction}")

        response_data = {"answer": prediction}
        return JSONResponse(response_data)
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return JSONResponse(content={"error": str(e)})

@app.post("/get_specialization")
async def get_specialization():
    pass

@app.post("/get_doctors")
async def get_doctors(request: DoctorRequest):
    urls= scrapeFromLocation(request.specialization, request.location)
    AgenticScrap(urls)

    dict_match= extract_dictionaries_from_file("results.txt")
    dictt=extract_dictionaries(dict_match)
    save_dictionaries_to_json(dictt, "doctors.json")
    adresses=extract_addresses_from_json("doctors.json")
    logging.info(f"User location: {request.user}")  # Log user object to check its structure

    m=create_map(adresses, GEOLOCATION_API, request.user)
    m.save('interactive_map.html')
    logging.info(f"Map has been saved to interactive_map.html")
    return {"message": "Map has been created"}

@app.post("/get_html")
async def get_html():
    try:
        return FileResponse("interactive_map.html", media_type="text/html")
    except Exception as e:
        logging.error(f"Failed to send the HTML file: {e}")
        return {"error": "File not found or another error occurred"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)