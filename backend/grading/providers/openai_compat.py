"""VLM provider backed by any OpenAI-compatible endpoint.

One client serves Gemini (Google's OpenAI-compatibility endpoint), OpenAI, and
self-hosted Modal/vLLM — the difference is only base_url + api_key + model, which
the registry pulls from settings.LLM_PROVIDERS. Images are sent as standard
`image_url` base64 data URIs and we request a JSON object response.

The caller is responsible for falling back to the mock on failure (see
orchestrator.run_vlm); we keep this provider thin.
"""

import json
import logging

from openai import BadRequestError, OpenAI

from . import base
from .. import prompts

log = logging.getLogger(__name__)

# Models that rejected `reasoning_effort` once (e.g. Gemma served via the Gemini
# OpenAI-compat endpoint answers 400 "Thinking level is not supported"). We
# remember them per worker process so we only pay the failed round-trip once and
# skip the knob thereafter. Module-level so it survives provider re-creation.
_NO_REASONING_MODELS: set[str] = set()


class OpenAICompatVLM(base.VLMProvider):
    def __init__(self, name, base_url, api_key, model, timeout=30.0, reasoning_effort=""):
        self.name = name
        self.model = model
        self.reasoning_effort = reasoning_effort or ""
        self._client = OpenAI(
            base_url=base_url or None,
            api_key=api_key or "missing",
            timeout=timeout,
            max_retries=1,
        )

    def grade(self, req: base.VLMRequest) -> dict:
        messages = prompts.build_vlm_messages(req)
        base_kwargs = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }
        # Curb "thinking" latency on models that support it (e.g. gemini-2.5-flash).
        # Sent via extra_body so non-supporting OpenAI-compatible servers ignore it.
        # Some models (e.g. Gemma) actively reject it with a 400; we detect that
        # once, remember it, and retry/skip without the knob so grading never breaks.
        want_effort = bool(self.reasoning_effort) and self.model not in _NO_REASONING_MODELS
        kwargs = dict(base_kwargs)
        if want_effort:
            kwargs["extra_body"] = {"reasoning_effort": self.reasoning_effort}
        try:
            resp = self._client.chat.completions.create(**kwargs)
        except BadRequestError as exc:
            if not (want_effort and _is_reasoning_rejection(exc)):
                raise
            _NO_REASONING_MODELS.add(self.model)
            log.info(
                "VLM model %r rejected reasoning_effort; retrying without it",
                self.model,
            )
            resp = self._client.chat.completions.create(**base_kwargs)
        content = (resp.choices[0].message.content or "").strip()
        data = _loads(content)
        data["source"] = self.name
        return prompts.normalize_vlm_output(data, n_uploaded=len(req.uploaded or []))


def _is_reasoning_rejection(exc: BadRequestError) -> bool:
    """True when a 400 is specifically about an unsupported thinking/reasoning knob."""
    msg = str(getattr(exc, "message", "") or exc).lower()
    return "thinking" in msg or "reasoning" in msg


def _loads(content: str) -> dict:
    """Parse model JSON; tolerate ```json fenced blocks some models still emit."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    if "```" in content:
        inner = content.split("```", 2)
        if len(inner) >= 2:
            body = inner[1]
            if body.startswith("json"):
                body = body[4:]
            try:
                return json.loads(body.strip())
            except json.JSONDecodeError:
                pass
    # Last resort: grab the outermost {...}.
    start, end = content.find("{"), content.rfind("}")
    if 0 <= start < end:
        try:
            return json.loads(content[start : end + 1])
        except json.JSONDecodeError:
            pass
    raise ValueError("VLM did not return valid JSON")
