import pytest
from unittest.mock import patch, MagicMock
from src.main import process_emails


@pytest.mark.asyncio
async def test_process_emails_empty():
    # Mock gws to return empty
    with patch('src.main.GmailIngestor') as MockIngestor:
        mock_instance = MagicMock()
        mock_instance.fetch_recent_emails.return_value = []
        MockIngestor.return_value = mock_instance

        result = await process_emails(max_results=1)
    assert isinstance(result, dict)
