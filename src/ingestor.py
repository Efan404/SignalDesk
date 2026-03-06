"""Email ingestor using gws CLI"""
import subprocess
import json
import uuid
import base64
import logging
from datetime import datetime, timezone
from src.models import EmailEvent

logger = logging.getLogger(__name__)


class GmailIngestor:
    """Fetch emails from Gmail using gws CLI"""

    def __init__(self):
        self.provider = "gmail"

    def fetch_recent_emails(self, max_results: int = 10) -> list[EmailEvent]:
        """Fetch recent emails from Gmail"""
        if max_results < 1 or max_results > 100:
            max_results = 10
        cmd = [
            "gws", "gmail", "users", "messages", "list",
            "--params", json.dumps({"maxResults": max_results, "q": "is:unread"})
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            raise RuntimeError(f"gws failed: {result.stderr}")

        messages = json.loads(result.stdout).get("messages", [])
        events = []

        for msg in messages:
            event = self._fetch_message(msg["id"])
            if event:
                events.append(event)

        return events

    def _fetch_message(self, message_id: str) -> EmailEvent | None:
        """Fetch single message details"""
        cmd = [
            "gws", "gmail", "users", "messages", "get",
            "--params", json.dumps({"id": message_id, "format": "full"})
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            logger.warning(f"Failed to fetch message {message_id}: {result.stderr}")
            return None

        data = json.loads(result.stdout)

        # Parse headers
        headers = data.get("payload", {}).get("headers", [])
        header_dict = {h["name"].lower(): h["value"] for h in headers}

        # Extract body
        body_text = self._extract_body(data.get("payload", {}))

        # Parse timestamp
        ts = data.get("internalDate", "0")
        timestamp = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)

        return EmailEvent(
            event_id=str(uuid.uuid4()),
            provider=self.provider,
            thread_id=data.get("threadId", ""),
            message_id=message_id,
            from_addr=header_dict.get("from", ""),
            to_addr=header_dict.get("to", ""),
            subject=header_dict.get("subject", ""),
            timestamp=timestamp,
            cc_addr=header_dict.get("cc", ""),
            body_text=body_text,
            permalink=f"https://mail.google.com/mail?ui=1&message_id={message_id}"
        )

    def _extract_body(self, payload: dict) -> str:
        """Extract text body from email payload"""
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                if "parts" in part:
                    result = self._extract_body(part)
                    if result:
                        return result
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        return ""
