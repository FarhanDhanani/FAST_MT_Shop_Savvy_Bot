import json
import streamlit as st
import requests
from tqdm import tqdm
from overrides import overrides
from typing import Any, Dict, List, Mapping, Optional

from langchain_core.embeddings import Embeddings
from langchain_core.pydantic_v1 import BaseModel, Extra

from langchain_openai import OpenAIEmbeddings
from config import Config

OLLAMA_EMBED_URL = "/api/embeddings"
EMBEDDING_MODEL_NAME = "mxbai-embed-large"
OPEN_AI_EMBED_MODEL_NAME = "text-embedding-3-small"

class CustomEmbedder(BaseModel, Embeddings):

    """
    Example:
        .. code-block:: python

            from solutions.embedder import CustomEmbedder
            emb = CustomEmbedder(
                model="llama:7b",
            )
            r1 = emb.embed_documents(
                [
                    "Alpha is the first letter of Greek alphabet",
                    "Beta is the second letter of Greek alphabet",
                ]
            )
            r2 = emb.embed_query(
                "What is the second letter of Greek alphabet"
            )
    """
    
    model: str

    base_url: str = "http://localhost:11434"
    """Default localhost URL for OLLAMA."""

    embed_instruction: str = "passage: "
    """Instruction used to embed documents."""

    query_instruction: str = "query: "
    """Instruction used to embed the query."""

    show_progress: bool = False
    """Whether to show a tqdm progress bar. Must have `tqdm` installed."""

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling Ollama."""
        return {
            "model": self.model,
        }

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {**{"model": self.model}, **self._default_params}

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    def _process_emb_response(self, input: str) -> List[float]:
        headers = {
            "Content-Type": "application/json",
        }

        try:
            res = requests.post(
                f"{self.base_url}"+OLLAMA_EMBED_URL,
                headers=headers,
                json={"model": self.model, "prompt": input, **self._default_params},
            )
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error raised by inference endpoint: {e}")

        if res.status_code != 200:
            raise ValueError(
                "Error raised by inference API HTTP code: %s, %s"
                % (res.status_code, res.text)
            )
        try:
            t = res.json()
            return t["embedding"]
        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(
                f"Error raised by inference API: {e}.\nResponse: {res.text}"
            )

    def _embed(self, input: List[str]) -> List[List[float]]:
        if self.show_progress:
            try:
                iter_ = tqdm(input, desc="OllamaEmbeddings")
            except ImportError:
                logger.warning(
                    "Unable to show progress bar because tqdm could not be imported. "
                    "Please install with `pip install tqdm`."
                )
                iter_ = input
        else:
            iter_ = input
        return [self._process_emb_response(prompt) for prompt in iter_]

    @overrides
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        instruction_pairs = [f"{self.embed_instruction}{text}" for text in texts]
        embeddings = self._embed(instruction_pairs)
        return embeddings

    @overrides
    def embed_query(self, text: str) -> List[float]:
        """
        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        instruction_pair = f"{self.query_instruction}{text}"
        embedding = self._embed([instruction_pair])[0]
        return embedding

embeddings = OpenAIEmbeddings(model=OPEN_AI_EMBED_MODEL_NAME,  openai_api_key=st.secrets["OPEN_AI_KEY"]) if Config.USE_OPEN_AI_EMBEDDER else CustomEmbedder(model=EMBEDDING_MODEL_NAME)