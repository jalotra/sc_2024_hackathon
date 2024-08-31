from typing import List
from fastapi import APIRouter
from ..redis_database import find_sets_with_member, pool
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import UploadFile, Depends
from .UserRoutes import read_user
from .DocumentRoutes import (
    create_document,
    create_redis_document,
    create_redis_document_set,
    match_document,
    read_document,
    read_redis_document,
)
from fastapi.exceptions import HTTPException
import aiofiles
import uuid
from ..models.Document import Document, RedisDocument
from pathlib import Path
import magic
from ..connectors import pdf, docs, slides, text
from .DocumentRoutes import get_db, get_redis_db
from src.main import create_RAG
import pickle
from ..main import load_rag, ask_question
from ..raptor.visualise import visual
from ..raptor.tree_structures import Node

rag_router = APIRouter()


def read_file_from_extension(file_path: str) -> str:
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Not able to find file at location : {file_path}")
    mime = magic.from_file(file_path, mime=True)
    print(f"File Path : {file_path} and Mime  is : {mime}")
    if (
        mime
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        return docs.DocParser().parse(file_path)
    elif mime in ["text/plain", "text/html"]:
        return text.TextParser().parse(file_path)
    elif (
        mime
        == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ):
        return slides.PptParser().parse(file_path)
    elif mime == "application/pdf":
        return pdf.PdfParser().parse(file_path)
    else:
        raise Exception(f"MimeType : {mime} not supported by the system to be parsed !")


@rag_router.post("/rag/add_document")
async def add_document(files: List[UploadFile], user_id: int):
    user = read_user(db=next(get_db()), user_id=user_id)
    if user is None:
        raise HTTPException("Not able to find the user")

    db_document_list = []
    for file in files:
        file_name = str(uuid.uuid4()) + "_" + file.filename
        async with aiofiles.open(f"/tmp/{file_name}", "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        # Now write this to be rag'ed document into redis
        redisDocument = RedisDocument(
            key=file_name, value=read_file_from_extension(f"/tmp/{file_name}")
        )

        redis_document_id = create_redis_document(
            redis_conn=next(get_redis_db()),
            document_key=redisDocument.key,
            document_value=redisDocument.value,
        )
        db_document = create_document(
            namespace_id=user.namespace_id,
            user_id=user_id,
            redis_document_id=redis_document_id,
            is_parsed=True,
            db=next(get_db()),
        )
        db_document_list.append(db_document)
    return JSONResponse(content=jsonable_encoder(db_document_list))


class DocumentRequest(BaseModel):
    ids: List[int]


@rag_router.post("/rag/build_save_tree")
def build_rag(document_ids: DocumentRequest, user_id: int):
    document_dbs : List[Document] = []
    for document_id in document_ids.ids:
        document_db = read_document(db=next(get_db()), document_id=document_id)
        if document_db is None:
            raise Exception(f"Not able to find document with id : {document_id}")
        elif document_db.user_id != user_id:
            raise Exception(
                f"Invalid Authorisation, userId : {user_id} can't see document : {document_id}"
            )
        document_dbs.append(document_db)

    redis_documents = [
        str(
            read_redis_document(
                redis_conn=next(get_redis_db()), document_key=x.redis_document_id
            ).value
        )
        for x in document_dbs
    ]
    RAG = create_RAG(redis_documents)

    rag_save_redis_key = f"RAG_{str(uuid.uuid4())}"
    value = pickle.dumps(RAG.tree)

    create_redis_document(
        redis_conn=next(get_redis_db()),
        document_key=rag_save_redis_key,
        document_value=value,
    )

    # Also write what all documents are part of some RAG_TREE
    # Create a reverse index
    for document in document_dbs:
        create_redis_document_set(
            redis_conn=next(get_redis_db()),
            document_key=rag_save_redis_key,
            document_value=document.redis_document_id
            )

    return {"rag_id": rag_save_redis_key}


@rag_router.get("/rag/getAllTreesThatIcouldbePartOf")
def getAllTreesThatIcouldbePartOf(document_name : str):
    matched_documents = match_document(
        next(get_db()),
        document_name
    )
    
    if matched_documents is None or len(matched_documents) == 0:
        return {
            "Error" : "No tree could which was build on it !"
        }

    # Now find all the trees that I could be a part of 
    matched_tree_ids = []
    for document in matched_documents:
        redis_document_id = document.redis_document_id
        print(redis_document_id)
        # Now match all the keys in redis-sets that have this redis_document_id as a member
        matched_tree_ids = find_sets_with_member(next(get_redis_db()), redis_document_id)

    return {
        "matched tree ids" : matched_tree_ids
    }

    

@rag_router.get("/rag/load_tree_and_QA")
def load_rag_and_QA(tree_id: str, question: str):
    redis_picked_tree = read_redis_document(
        redis_conn=next(get_redis_db()), document_key=tree_id
    )
    if redis_picked_tree is None:
        raise Exception(f"No tree found with tree id : {tree_id}")

    tree = pickle.loads(redis_picked_tree.value)
    RAG = load_rag(tree)
    return ask_question(RAG=RAG, question=question)

@rag_router.get("/rag/print_tree")
def load_rag_and_QA(tree_id: str):
    redis_picked_tree = read_redis_document(
        redis_conn=next(get_redis_db()), document_key=tree_id
    )
    if redis_picked_tree is None:
        raise Exception(f"No tree found with tree id : {tree_id}")

    tree = pickle.loads(redis_picked_tree.value)
    return (tree.root_nodes[list(tree.root_nodes.keys())[0]]).__repr__()

@rag_router.get("/rag/show_tree")
def load_rag_and_QA(tree_id: str):
    redis_picked_tree = read_redis_document(
        redis_conn=next(get_redis_db()), document_key=tree_id
    )
    if redis_picked_tree is None:
        raise Exception(f"No tree found with tree id : {tree_id}")

    tree = pickle.loads(redis_picked_tree.value)
    root_node = Node(
        text = "This is placeholder fellas; made for my ease !",
        index= -1, 
        children=tree.root_nodes, 
        embeddings=[]
    )

    visual(root_node, tree)