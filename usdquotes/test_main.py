from typer.testing import CliRunner

from .main import app

runner = CliRunner()

def test_app():
    result = runner.invoke(app, ["19560131"])
    assert result.exit_code == 0
