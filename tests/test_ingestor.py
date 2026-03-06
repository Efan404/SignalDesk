import pytest
from src.ingestor import GmailIngestor

def test_gmail_ingestor_initialization():
    ingestor = GmailIngestor()
    assert ingestor.provider == "gmail"
