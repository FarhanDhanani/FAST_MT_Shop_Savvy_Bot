import json
import requests
from tqdm import tqdm
from overrides import overrides
from typing import Any, List, Mapping, Optional
from langchain_community.chat_models import ChatOllama
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM

OLLAMA_LLM_URL = "/api/generate"
MODEL_NAME = "llama3"
CYPHER_MODEL_NAME = "codegemma"

class CustomLLM(LLM):
    """
    Example:
        .. code-block:: python
            from solutions.llm import CustomLLM
            from solutions.llm import MODEL_NAME
            
            llm = CustomLLM(model=MODEL_NAME)
            response = llm.invoke(message)
    """
    base_url:str = "http://localhost:11434";
    model:str;

    @property
    def _llm_type(self) -> str:
        return self.model;

    @overrides
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        # if stop is not None:
        #     raise ValueError("stop kwargs are not permitted.")
        
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(url=f"{self.base_url}"+OLLAMA_LLM_URL,
                                 headers=headers, 
                                 data=self._getFormattedData(prompt))
        t = response.json()

        return t["response"]

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "url":self.base_url,
            "model": self.model,
        }
    
    def _getFormattedData(self, prompt:str)-> str:
        return json.dumps({
            "model": self.model,
            "prompt": prompt,
             "stream": False 
        })

llm  = CustomLLM(model=MODEL_NAME)
cypher_llm = CustomLLM(model=CYPHER_MODEL_NAME)
#llm = ChatOllama(model=MODEL_NAME) #CustomLLM(model=MODEL_NAME)