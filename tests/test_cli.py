def test_cli_has_bot_command():
    from click.testing import CliRunner
    from src.cli import cli
    result = CliRunner().invoke(cli, ["--help"])
    assert "bot" in result.output
