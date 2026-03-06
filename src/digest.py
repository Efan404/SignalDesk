"""Daily Digest Generator"""
from src.models import TriageDecision, EmailEvent, RouteType


class DigestGenerator:
    """Generate daily digest from triage decisions"""

    def generate(self, decisions: list[TriageDecision],
                 events: dict[str, EmailEvent]) -> str:
        """Generate digest text"""
        if not decisions:
            return "📭 No emails to digest today."

        lines = ["📬 *Daily Digest*\n"]

        # Group by route
        push_high = [d for d in decisions if d.route == RouteType.PUSH_HIGH]
        push_normal = [d for d in decisions if d.route == RouteType.PUSH_NORMAL]
        digest = [d for d in decisions if d.route == RouteType.DIGEST_EVENING]
        silent = [d for d in decisions if d.route == RouteType.SILENT]
        delegate = [d for d in decisions if d.route == RouteType.DELEGATE]

        if push_high:
            lines.append("🔥 *Urgent*")
            for d in push_high:
                e = events.get(d.event_id)
                if e:
                    lines.append(f"  • {e.subject} ({d.reasons[0] if d.reasons else ''})")
            lines.append("")

        if digest:
            lines.append("📌 *Important*")
            for d in digest:
                e = events.get(d.event_id)
                if e:
                    lines.append(f"  • {e.subject}")
            lines.append("")

        if delegate:
            lines.append("✍️ *To Review*")
            for d in delegate:
                e = events.get(d.event_id)
                if e:
                    lines.append(f"  • {e.subject}")
            lines.append("")

        if silent:
            lines.append(f"💤 {len(silent)} other items (silent)")

        return "\n".join(lines)
