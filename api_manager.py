import requests
import time
import json
import base64
import numpy as np
from typing import List, Optional, Dict, Any, Union

class APIManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.embed_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        self.chat_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _request_with_backoff(self, url: str, payload: Dict[str, Any], max_retries: int = 5) -> Optional[Dict[str, Any]]:
        wait_time = 1.0
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=self.headers, timeout=60, verify=False)
                
                if response.status_code == 200:
                    return response.json()
                
                elif response.status_code == 429:
                    print(f"[API] 429 Rate Limit hit. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                
                elif 500 <= response.status_code < 600:
                    print(f"[API] Server error {response.status_code}. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                
                else:
                    print(f"[API] Critical error: {response.status_code} - {response.text}")
                    return None
                
            except requests.exceptions.RequestException as e:
                print(f"[API] Network exception: {str(e)}. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
            
            time.sleep(wait_time)
            wait_time *= 2
            
        print("[API] Maximum retries reached. Request failed.")
        return None

    def get_embeddings(self, texts: List[str], batch_size: int = 25) -> Optional[np.ndarray]:
        if not texts:
            return np.array([])

        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload = {
                "model": "text-embedding-v3",
                "input": {"texts": batch}
            }
            
            res = self._request_with_backoff(self.embed_url, payload)
            if res and "output" in res and "embeddings" in res["output"]:
                embeddings = [item["embedding"] for item in res["output"]["embeddings"]]
                all_embeddings.extend(embeddings)
            else:
                print(f"[API] Failed to get embeddings for batch {i//batch_size + 1}")
                return None
                
        return np.array(all_embeddings)

    def get_llm_response(self, prompt: str, temperature: float = 0.5) -> Optional[str]:
        payload = {
            "model": "qwen3.5-plus",
            "input": {
                "messages": [{"role": "user", "content": prompt}]
            },
            "parameters": {
                "temperature": temperature,
                "result_format": "message"
            }
        }
        
        res = self._request_with_backoff(self.chat_url, payload)
        if res and "output" in res and "choices" in res["output"]:
            return res["output"]["choices"][0]["message"]["content"]
        
        return None

class KeyObfuscator:
    @staticmethod
    def obfuscate(key: str) -> str:
        if not key: return ""
        return base64.b64encode(key.encode()).decode()

    @staticmethod
    def deobfuscate(obfuscated_key: str) -> str:
        if not obfuscated_key: return ""
        try:
            return base64.b64decode(obfuscated_key.encode()).decode()
        except Exception:
            return obfuscated_key
