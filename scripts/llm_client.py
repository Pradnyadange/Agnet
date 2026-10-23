import json
import os
import re
import sys
import requests

try:
    from common import compute_sha256_text
except ImportError:
    from scripts.common import compute_sha256_text

def extract_and_parse_json(text: str) -> dict:
    """Strip markdown fences and parse JSON strictly."""
    cleaned = text.strip()
    # Strip markdown code blocks ```json ... ``` or ``` ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()
    return json.loads(cleaned)

class LLMClient:
    def __init__(self, provider: str, model_id: str, base_url: str | None = None):
        if not model_id:
            raise ValueError("Explicit model_id is required.")
        self.provider = provider
        self.model_id = model_id
        self.base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_card_url = f"https://ollama.com/library/{model_id.split(':')[0]}"
        self.license_text, self.license_sha256 = self._fetch_license()
        self.failure_count = 0

    def _fetch_license(self) -> tuple[str, str]:
        """Read license text from model metadata, compute sha256, never infer from model name."""
        if self.provider == "ollama":
            try:
                resp = requests.post(f"{self.base_url}/api/show", json={"name": self.model_id}, timeout=10)
                if resp.status_code == 200:
                    lic = resp.json().get("license", "").strip()
                    if lic:
                        return lic, compute_sha256_text(lic)
            except Exception:
                pass
        return f"unknown, see model_card_url ({self.model_card_url})", "unknown"


    def generate_json(self, prompt: str, system_prompt: str = "") -> tuple[dict | None, str]:
        """
        Query provider for JSON response. Retries once if JSON is malformed.
        Returns (parsed_dict, raw_response_text).
        """
        raw_response = ""
        for attempt in range(2):
            try:
                if self.provider == "ollama":
                    raw_response = self._call_ollama(prompt, system_prompt)
                elif self.provider == "hosted":
                    raw_response = self._call_hosted(prompt, system_prompt)
                else:
                    raise ValueError(f"Unknown provider: {self.provider}")
                
                parsed = extract_and_parse_json(raw_response)
                return parsed, raw_response
            except Exception as e:
                self.failure_count += 1
                if attempt == 0:
                    prompt = f"{prompt}\n\nIMPORTANT: Your previous response was not valid JSON. You MUST return ONLY a valid, raw JSON object matching the requested schema without markdown fences or any explanation."
                else:
                    sys.stderr.write(f"LLM generation failed after retry: {e}\n")
                    return None, raw_response
        return None, raw_response

    def _call_ollama(self, prompt: str, system_prompt: str) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "format": "json"
        }
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")

    def _call_hosted(self, prompt: str, system_prompt: str) -> str:
        # Hosted provider reads API key from environment variable
        api_key = os.environ.get("HOSTED_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Hosted mode requires HOSTED_API_KEY or OPENAI_API_KEY environment variable")
            
        endpoint = os.environ.get("HOSTED_API_ENDPOINT", "https://api.openai.com/v1/chat/completions")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
