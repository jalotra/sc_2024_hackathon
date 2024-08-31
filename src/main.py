from typing import List, Optional
from src.raptor import RetrievalAugmentation, RetrievalAugmentationConfig
from src.raptor import (
    BaseEmbeddingModel,
    BaseQAModel,
    BaseSummarizationModel,
    BaseRetriever,
)
from sentence_transformers import SentenceTransformer
import requests
from tenacity import retry, stop_after_attempt, wait_random_exponential
import multiprocessing


class EmbeddingModel(BaseEmbeddingModel):
    sbert_model_name = "multi-qa-mpnet-base-cos-v1"

    def create_embedding(self, text):
        model = SentenceTransformer(model_name_or_path=self.sbert_model_name)
        # pool = model.start_multi_process_pool(['cpu'] * multiprocessing.cpu_count())
        # return model.encode_multi_process(text, pool=pool)
        return model.encode(text)


class QAModel(BaseQAModel):
    model_name = "gpt-3.5-turbo"

    def __init__(self) -> None:
        model_params = {
            "max_tokens": 5000,
            "topP": 1,
            "temperature": 0,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "model_name": self.model_name,
        }

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def answer_question(self, context, question):
        try:
            url = "localhost:11434"
            response = requests.post(
                url=f"http://{url}/api/chat",
                data={
                    "model": self.model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are Question Answering Portal",
                        },
                        {
                            "role": "user",
                            "content": f"Given Context: {context} Give the best full answer amongst the option to question {question}",
                        },
                    ],
                },
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(e)
            return e


class SummarisationModel(BaseSummarizationModel):
    def __init__(self, model="gemma:7b"):
        self.model = model

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def summarize(self, context, max_tokens=500, stop_sequence=None):

        try:
            url = "localhost:11434"
            response = requests.post(
                url=f"http://{url}/api/chat",
                data={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {
                            "role": "user",
                            "content": f"Write a summary of the following, including as many key details as possible: {context}:",
                        },
                    ],
                },
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(e)
            return e


def load_rag(tree, config=None):
    if config is None:
        config = RetrievalAugmentationConfig(embedding_model=EmbeddingModel())
    return RetrievalAugmentation(config=config, tree=tree)


def create_RAG(documents: List[str]) -> RetrievalAugmentation:
    RAG = RetrievalAugmentation(
        config=RetrievalAugmentationConfig(embedding_model=EmbeddingModel())
    )
    for doc in documents:
        RAG.add_documents(doc)

    print(RAG)

    return RAG


def ask_question(RAG: RetrievalAugmentation, question: str) -> str:
    return RAG.answer_question(question=question)
