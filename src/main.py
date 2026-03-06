"""Main orchestration"""
import asyncio
from src.ingestor import GmailIngestor
from src.triage import TriageEngine
from src.digest import DigestGenerator
from src.notifier import TelegramNotifier
from src.db import get_db, init_db


async def process_emails(max_results: int = 10) -> dict:
    """Main processing pipeline"""
    init_db()

    # 1. Fetch emails
    ingestor = GmailIngestor()
    emails = ingestor.fetch_recent_emails(max_results)

    if not emails:
        return {"status": "no_emails", "processed": 0}

    # 2. Triage each email
    engine = TriageEngine()
    decisions = []
    events_map = {e.event_id: e for e in emails}

    for email in emails:
        decision = await engine.triage(email)
        decisions.append(decision)

        # Save to DB
        db = get_db()
        db.execute("""
            INSERT OR REPLACE INTO email_events
            (event_id, provider, thread_id, message_id, from_addr, to_addr, cc_addr, subject, timestamp, body_text, permalink)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (email.event_id, email.provider, email.thread_id, email.message_id,
              email.from_addr, email.to_addr, email.cc_addr, email.subject,
              email.timestamp.isoformat(), email.body_text, email.permalink))

        db.execute("""
            INSERT OR REPLACE INTO triage_decisions
            (event_id, importance, urgency, delegatable, needs_user_decision, reasons, evidence_refs, route)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (decision.event_id, decision.importance, decision.urgency,
              int(decision.delegatable), int(decision.needs_user_decision),
              ",".join(decision.reasons), ",".join(decision.evidence_refs),
              decision.route.value))
        db.commit()
        db.close()

    # 3. Generate digest
    generator = DigestGenerator()
    digest = generator.generate(decisions, events_map)

    # 4. Send notification
    notifier = TelegramNotifier()
    notifier.send_sync(digest)

    return {
        "status": "success",
        "processed": len(emails),
        "digest": digest
    }


if __name__ == "__main__":
    asyncio.run(process_emails())
