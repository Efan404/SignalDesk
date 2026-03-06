"""Email ingestor using gws CLI"""
import subprocess
import json
import uuid
from datetime import datetime, timezone
from src.models import EmailEvent


class GmailIngestor:
    """Fetch emails from Gmail using gws CLI"""

    def __init__(self):
        self.provider = "gmail"

    def fetch_recent_emails(self, max_results: int = 10) -> list[EmailEvent]:
        """Fetch recent emails from Gmail"""
        cmd = [
            "gws", "gmail", "users", "messages", "list",
            "--params", json.dumps({"maxResults": max_results, "q": "is:unread"})
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

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
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
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
            cc_addr=header_dict.get("cc", ""),
            subject=header_dict.get("subject", ""),
            timestamp=timestamp,
            body_text=body_text,
            permalink=f"https://mail.google.com/mail?ui=1&message_id={message_id}"
        )

    def _extract_body(self, payload: dict) -> str:
        """Extract text body from email payload"""
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    return part.get("body", {}).get("data", "")
                if "parts" in part:
                    result = self._extract_body(part)
                    if result:
                        return result
        return payload.get("body", {}).get("data", "")
