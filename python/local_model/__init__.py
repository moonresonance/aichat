import requests
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from transformers import T5Tokenizer
from modelscope.pipelines import pipeline as modelscope_pipeline
from modelscope.utils.constant import Tasks
from modelscope.models.nlp import T5ForConditionalGeneration
from modelscope.preprocessors import TextGenerationTransformersPreprocessor
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_ollama import OllamaLLM


class LocalModel:
    def __init__(self, model_path, config):
        self.model_path = model_path
        self.config = config

    def load_model(self):
        tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        model = AutoModelForCausalLM.from_pretrained(self.model_path).to(self.config)

        # 修正1：使用小写的 pipeline 函数
        # 修正2：device 参数应放在 model_kwargs 中
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=self.config if self.config == "cuda" else -1  # -1 表示 CPU
        )

        llm = HuggingFacePipeline(pipeline=pipe)
        return llm

    def load_ollama(self, model_name):
        # 修正3：新版本 Ollama 可能不支持 device 参数
        # 方案1：完全移除 device 参数
        # llm = OllamaLLM(model=model_name)

        # 或者方案2：如果确实需要指定设备，尝试以下方式
        llm = OllamaLLM(
            model=model_name,
            model_kwargs={"device": self.config}  # 取决于新版本是否支持
        )
        return llm

    def load_qwe3(self, ip, message):
        payload = {
            "model": "qwen3",
            "messages": message,
            "max_tokens": 20000,
        }
        resp = requests.post(ip, json=payload, timeout=200)
        resp.raise_for_status()
        data = resp.json()
        result = data["choices"][0]["message"]["content"]
        return result

