"""LLM-based Triage Engine"""
import json
import logging
import httpx
from src.config import Config
from src.models import EmailEvent, TriageDecision, RouteType

logger = logging.getLogger(__name__)


class TriageEngine:
    """Use LLM to classify emails"""

    SYSTEM_PROMPT = """You are an email triage assistant. Analyze each email and classify it.

Output JSON with these fields:
- importance: 0-3 (3=most important for goals/key people/projects)
- urgency: 0-3 (3=time-critical, e.g., within 2h; 2=EOD; 1=within 3d)
- delegatable: true/false (can an AI produce a draft reply?)
- needs_user_decision: true/false (requires your judgment/authorization/stance)
- reasons: list of 1-3 short reasons
- evidence_refs: list of evidence (e.g., "subject line", "from address")

Rules:
- Security/account/payment keywords → urgency=3, push
- Requests for commitment (time/money/resources) → needs_user_decision=true
- Auto-notifications → delegatable=true, importance=0-1
"""

    def __init__(self):
        config = Config()
        self.base_url = config.litellm_base_url
        self.api_key = config.litellm_api_key
        self.model = f"openai/{config.litellm_model}"

    async def triage(self, email: EmailEvent) -> TriageDecision:
        """Run triage on a single email"""
        user_prompt = f"""From: {email.from_addr}
To: {email.to_addr}
Subject: {email.subject}

{email.body_text[:2000]}"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            triage_data = json.loads(content)

        return self._build_decision(email.event_id, triage_data)

    def _build_decision(self, event_id: str, data: dict) -> TriageDecision:
        """Convert LLM output to TriageDecision"""
        route = self._determine_route(
            data.get("importance", 0),
            data.get("urgency", 0),
            data.get("delegatable", False),
            data.get("needs_user_decision", False)
        )

        return TriageDecision(
            event_id=event_id,
            importance=data.get("importance", 0),
            urgency=data.get("urgency", 0),
            delegatable=data.get("delegatable", False),
            needs_user_decision=data.get("needs_user_decision", False),
            reasons=data.get("reasons", []),
            evidence_refs=data.get("evidence_refs", []),
            route=route
        )

    def _determine_route(self, importance: int, urgency: int,
                        delegatable: bool, needs_decision: bool) -> RouteType:
        """Determine route based on I/U/A/D"""
        if delegatable and not needs_decision:
            return RouteType.DELEGATE

        if importance >= 2 and urgency >= 2:
            return RouteType.PUSH_HIGH
        if urgency >= 2 and importance < 2:
            return RouteType.PUSH_NORMAL
        if importance >= 2 and urgency < 2:
            return RouteType.DIGEST_EVENING
        return RouteType.SILENT
