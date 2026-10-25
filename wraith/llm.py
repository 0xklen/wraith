"""Tiny OpenAI-compatible chat client (stdlib only).

Works with OpenAI, DeepSeek, OpenRouter, Anthropic-compatible and
Gemini-compatible gateways, and any local server that speaks
`POST /chat/completions`. No third-party dependencies.
"""
import base64
import json
import urllib.error
import urllib.request

from .prompts import SYSTEM_PROMPT


def parse_action(raw):
    """Pull the first JSON object out of a model reply (fences tolerated)."""
    raw = raw.strip()
    if raw.startswith('```'):
        raw = raw.strip('`')
        if raw.startswith('json'):
            raw = raw[4:]
    i = raw.find('{')
    j = raw.rfind('}')
    if i >= 0 and j > i:
        raw = raw[i:j + 1]
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError('LLM returned invalid JSON: ' + raw[:200]) from e


class LLM:
    def __init__(self, base_url, api_key, model, temperature=0.0):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    def chat(self, messages, timeout=90):
        body = json.dumps({
            'model': self.model,
            'messages': messages,
            'temperature': self.temperature,
        }).encode('utf-8')
        req = urllib.request.Request(
            self.base_url + '/chat/completions',
            data=body,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.api_key,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                j = json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f'LLM HTTP {e.code}: {e.read().decode("utf-8", "ignore")[:300]}') from e
        return j['choices'][0]['message']['content']

    def plan(self, task, screenshot_bytes, history):
        """Turn a task + screenshot + action history into the next action dict."""
        img = base64.b64encode(screenshot_bytes).decode('ascii')
        user_content = [{'type': 'text', 'text': 'TASK: ' + task}]
        if history:
            user_content.append(
                {'type': 'text', 'text': 'Actions so far: ' + json.dumps(history[-12:])})
        user_content.append(
            {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + img}})
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_content},
        ]
        raw = self.chat(messages)
        return parse_action(raw)
