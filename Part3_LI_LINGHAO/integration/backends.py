"""One network boundary, used only after an explicit live selection."""
import json
import os
import urllib.request
from copy import deepcopy


class ScriptedBackend:
    name = "scripted"

    def __init__(self, steps):
        self.steps = iter(deepcopy(steps))

    def next_move(self, transcript):
        # Synthetic instrumentation only; billed API cost is zero.
        return next(self.steps), {"prompt_tokens": 800, "completion_tokens": 60}


class LiveBackend:
    name = "live"

    def __init__(self, model, base_url):
        self.model, self.base_url = model, base_url

    def next_move(self, transcript):
        return _live_call(transcript, self.model, self.base_url)


def _live_call(transcript, model, base_url):
    """The only function aware of provider authentication and HTTP format."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("live requires OPENROUTER_API_KEY")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps({"model": model, "messages": [{"role": "user", "content": transcript}],
                         "temperature": 0, "max_tokens": 2000,
                         "stop": ["Observation:", "\nObservation:"]}).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.load(response)
    usage = payload.get("usage", {})
    for name in ("prompt_tokens", "completion_tokens"):
        if not isinstance(usage.get(name), int) or usage[name] < 0:
            raise ValueError("provider did not supply valid token usage")
    return payload["choices"][0]["message"]["content"], usage


def judge_call(messages, model, base_url, max_tokens=2400):
    """Judge transport: separate system instructions, no agent stop sequences."""
    key = os.environ.get('OPENROUTER_API_KEY')
    if not key:
        raise ValueError('Judge requires OPENROUTER_API_KEY')
    request = urllib.request.Request(
        base_url.rstrip('/') + '/chat/completions',
        data=json.dumps({'model': model, 'messages': messages,
                         'temperature': 0, 'max_tokens': max_tokens,
                         'response_format': {'type': 'json_object'}}).encode(),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)
