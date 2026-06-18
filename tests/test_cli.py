from typer.testing import CliRunner
from pathlib import Path
import tempfile
import json
import pytest

from promptverge.main import app

runner = CliRunner()


@pytest.fixture
def mock_cwd(mocker):
    """Fixture to create a temporary directory and mock Path.cwd() to use it."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        mocker.patch("promptverge.main.Path.cwd", return_value=temp_path)
        yield temp_path


def test_run_engineering_cli_file_not_found(prefect_test_harness):
    """
    Test the 'run-engineering' CLI command with a non-existent file.
    """
    result = runner.invoke(
        app,
        [
            "engineering",
            "non_existent_file.py",
            "This should fail.",
        ],
    )
    assert result.exit_code != 0
    assert "Invalid value for 'CODE_FILE'" in result.stdout
    assert "does not exist" in result.stdout


@pytest.mark.parametrize(
    "command, mock_path, mock_return_value_key, cli_args, expected_outputs, fixture_file",
    [
        (
            "engineering",
            "promptverge.flows.engineering_workflow.run_engineering_flow",
            "engineering_tuple",
            ["As a developer, I want to refactor this."],
            [
                "Executing engineering workflow...",
                "--- Workflow Complete ---",
                "Generated Code Audit Summary:",
                "Generated PRD Summary:",
                "Generated Task Summary:",
                "Outputs saved:",
            ],
            "dummy_code.py",
        ),
        (
            "knowledge",
            "promptverge.flows.knowledge_workflow.run_knowledge_flow",
            "quiz",
            [],
            [
                "Quiz generated successfully!",
                "Questions:",
                "Status:",
                "Tags:",
            ],
            "dummy_paper.txt",
        ),
    ],
)
def test_run_cli_command_success(
    mocker,
    mock_marvin_objects,
    mock_cwd,
    prefect_test_harness,
    command,
    mock_path,
    mock_return_value_key,
    cli_args,
    expected_outputs,
    fixture_file,
):
    """Test successful execution of CLI commands."""
    mock_return_value = (
        (
            mock_marvin_objects["audit"],
            mock_marvin_objects["prd"],
            mock_marvin_objects["task"],
        )
        if mock_return_value_key == "engineering_tuple"
        else mock_marvin_objects[mock_return_value_key]
    )
    mocker.patch(mock_path, return_value=mock_return_value)

    fixture_path = Path(__file__).parent / f"fixtures/{fixture_file}"
    invoke_args = [command, str(fixture_path)] + cli_args

    result = runner.invoke(app, invoke_args)

    assert result.exit_code == 0, f"CLI command failed with output: {result.stdout}"
    for expected_output in expected_outputs:
        assert expected_output in result.stdout


def test_run_knowledge_cli_triples_only(mocker, tmp_path, prefect_test_harness):
    """
    Test the 'run-knowledge' CLI command with --triples-only flag.
    """
    # Mock the extract_kg_triples function
    mock_triples = [("gene", "codes_for", "protein"), ("cell", "contains", "nucleus")]
    mocker.patch(
        "promptverge.flows.knowledge_workflow.extract_kg_triples",
        return_value=mock_triples,
    )

    fixture_path = Path(__file__).parent / "fixtures/dummy_paper.txt"
    result = runner.invoke(
        app,
        [
            "knowledge",
            str(fixture_path),
            "--triples-only",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, f"CLI command failed with output: {result.stdout}"
    assert "Executing knowledge extraction..." in result.stdout
    assert "Knowledge triples saved to" in result.stdout

    triples_files = list(tmp_path.glob("triples_*.json"))
    assert len(triples_files) == 1

    with open(triples_files[0]) as f:
        saved_triples = json.load(f)
    expected_triples = [list(triple) for triple in mock_triples]
    assert saved_triples == expected_triples


@pytest.mark.parametrize(
    "command, mock_path, mock_return_value_key, cli_args, fixture_file, expected_files_count",
    [
        (
            "engineering",
            "promptverge.flows.engineering_workflow.run_engineering_flow",
            "engineering_tuple",
            ["As a developer, I want to refactor this."],
            "dummy_code.py",
            3,
        ),
        (
            "knowledge",
            "promptverge.flows.knowledge_workflow.run_knowledge_flow",
            "quiz",
            [],
            "dummy_paper.txt",
            1,
        ),
    ],
)
def test_run_cli_command_with_custom_output_dir(
    mocker,
    mock_marvin_objects,
    tmp_path,
    prefect_test_harness,
    command,
    mock_path,
    mock_return_value_key,
    cli_args,
    fixture_file,
    expected_files_count,
):
    """Test CLI commands with a custom output directory."""
    mock_return_value = (
        (
            mock_marvin_objects["audit"],
            mock_marvin_objects["prd"],
            mock_marvin_objects["task"],
        )
        if mock_return_value_key == "engineering_tuple"
        else mock_marvin_objects[mock_return_value_key]
    )
    mocker.patch(mock_path, return_value=mock_return_value)

    custom_output_dir = tmp_path / "custom_outputs"
    fixture_path = Path(__file__).parent / f"fixtures/{fixture_file}"
    invoke_args = (
        [command, str(fixture_path)]
        + cli_args
        + ["--output-dir", str(custom_output_dir)]
    )

    result = runner.invoke(app, invoke_args)

    assert result.exit_code == 0, f"CLI command failed with output: {result.stdout}"
    assert custom_output_dir.exists()
    output_files = list(custom_output_dir.glob("*.json"))
    assert len(output_files) == expected_files_count


@pytest.mark.parametrize(
    "command, mock_path, cli_args, fixture_file, exception_text",
    [
        (
            "engineering",
            "promptverge.flows.engineering_workflow.run_engineering_flow",
            ["As a developer, I want to refactor this."],
            "dummy_code.py",
            "Test engineering exception",
        ),
        (
            "knowledge",
            "promptverge.flows.knowledge_workflow.run_knowledge_flow",
            [],
            "dummy_paper.txt",
            "Test knowledge exception",
        ),
        (
            "knowledge",
            "promptverge.flows.knowledge_workflow.extract_kg_triples",
            ["--triples-only"],
            "dummy_paper.txt",
            "Test triples exception",
        ),
    ],
)
def test_run_cli_command_exception_handling(
    mocker,
    prefect_test_harness,
    command,
    mock_path,
    cli_args,
    fixture_file,
    exception_text,
):
    """Test CLI command exception handling."""
    mocker.patch(mock_path, side_effect=Exception(exception_text))

    fixture_path = Path(__file__).parent / f"fixtures/{fixture_file}"
    invoke_args = [command, str(fixture_path)] + cli_args

    result = runner.invoke(app, invoke_args)

    assert "An unexpected error occurred:" in result.stdout
    assert exception_text in result.stdout
