import torch
from transformers import AutoTokenizer, AutomodelForCasualLM, pipeline
from typing import Dict
from huggingface_hub import login
import os

MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
DEFAULT_MAX_LENGTH = 128

class Model:

    def __init__(self, data_dir: string, config: Dict, **kwargs) -> None:
        self.data_dir = data_dir
        self._config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.pipeline = None
        secrets = kwargs.get("secrets")
        self.huggingface_api_token = "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"

    def load(self) -> None:
        login(token=self.huggingface_api_token)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth=self.huggingface_api_token)

        model_8bit = AutomodelForCasualLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            load_in_8bit=True,
            trust_remote_code=True
        )

        self.pipeline = pipeline(
            "text-generation",
            model = model_8bit,
            tokenizer = self.tokenizer,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            device_map="auto"
        )

    def predict(self, request: Dict) -> Dict:
        with torch.no_grad():
            try:
                prompt = request.pop("prompt")
                data = self.pipeline(
                    prompt,
                    eos_token_id=self.tokenizer.eos_token_id,
                    max_length=DEFAULT_MAX_LENGTH,
                    **request
                )[0]
                return {"data": data}
            except Exception as exc:
                return {"status": "error", "data": None, "message": str(exc)}
