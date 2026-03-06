"""Main orchestration"""
import asyncio
from src.ingestor import GmailIngestor
from src.triage import TriageEngine
from src.digest import DigestGenerator
from src.notifier import TelegramNotifier
from src.db import init_db, save_email_event, save_triage_decision


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

        # Save to DB using封装函数
        save_email_event(email)
        save_triage_decision(decision)

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
