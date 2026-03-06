"""CLI interface using Rich"""
import asyncio
import click
from rich.console import Console
from rich.table import Table
from src.main import process_emails
from src.db import get_db, init_db
from src.config import config
from src.bot import run_bot

console = Console()


@click.group()
def cli():
    """SignalDesk - Attention OS Personal Assistant"""
    pass


@cli.command()
@click.option("--max", default=10, help="Max emails to process")
def run(max):
    """Process emails and send digest"""
    console.print("[bold blue]Processing emails...[/bold blue]")
    result = asyncio.run(process_emails(max))
    console.print(f"[green]Processed {result['processed']} emails[/green]")


@cli.command()
def status():
    """Show recent triage decisions"""
    init_db()
    with get_db() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("""
            SELECT e.subject, t.importance, t.urgency, t.route, t.reasons
            FROM triage_decisions t
            JOIN email_events e ON t.event_id = e.event_id
            ORDER BY e.timestamp DESC
            LIMIT 20
        """).fetchall()

    table = Table(title="Recent Triage Decisions")
    table.add_column("Subject", style="cyan")
    table.add_column("I", justify="center")
    table.add_column("U", justify="center")
    table.add_column("Route", style="magenta")

    for row in rows:
        table.add_row(row[0][:50], str(row[1]), str(row[2]), row[3])

    console.print(table)


@cli.command()
def digest():
    """Manually trigger digest"""
    from src.ingestor import GmailIngestor
    from src.triage import TriageEngine
    from src.digest import DigestGenerator
    from src.notifier import TelegramNotifier

    console.print("[bold]Generating digest...[/bold]")

    emails = GmailIngestor().fetch_recent_emails(50)
    events_map = {e.event_id: e for e in emails}

    engine = TriageEngine()
    decisions = []
    for email in emails:
        decision = asyncio.run(engine.triage(email))
        decisions.append(decision)

    digest = DigestGenerator().generate(decisions, events_map)
    console.print(digest)

    notifier = TelegramNotifier()
    notifier.send_sync(digest)


@cli.command()
def bot():
    """Start Telegram bot"""
    console.print("[bold green]Starting SignalDesk Bot...[/bold green]")
    run_bot()


if __name__ == "__main__":
    cli()
