# FILE: cultivation/systems/PromptVerge/promptverge/main.py
"""Provides the command-line interface for the PromptVerge system."""

import typer
import json
import traceback
from datetime import datetime
from pathlib import Path
from rich import print



app = typer.Typer(
    name="promptverge",
    help="An AI-powered system for code-to-task and paper-to-quiz workflows.",
    add_completion=False,
)

@app.command("engineering")
def cli_run_engineering_flow(
    code_file: Path = typer.Argument(..., exists=True, dir_okay=False, help="Path to the source code file to analyze."),
    user_story: str = typer.Argument(..., help="The user story to guide PRD generation."),
    output_dir: Path = typer.Option(
        None, 
        "--output-dir", 
        help="The directory to save output files. Defaults to './cultivation/systems/PromptVerge/outputs'",
        writable=True,
        resolve_path=True
    )
):
    """Runs the full Code -> PRD -> Task engineering workflow."""
    from .flows import engineering_workflow

    try:
        print(f":gear:  Reading code from [bold cyan]{code_file}[/bold cyan]")
        code_content = code_file.read_text()

        print(":robot:  Executing engineering workflow...")
        audit, prd, task = engineering_workflow.run_engineering_flow(code_content, user_story)

        # Save outputs to files
        # Define output dir relative to the script file for robustness
        outputs_dir = output_dir or (Path(__file__).parent.parent / "outputs")
        outputs_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save as JSON files
        audit_file = outputs_dir / f"audit_{timestamp}.json"
        prd_file = outputs_dir / f"prd_{timestamp}.json"
        task_file = outputs_dir / f"task_{timestamp}.json"

        audit_file.write_text(audit.model_dump_json(indent=2))
        prd_file.write_text(prd.model_dump_json(indent=2))
        task_file.write_text(task.model_dump_json(indent=2))

        print("--- [bold green]Workflow Complete[/bold green] ---")
        print("\n:floppy_disk: [bold]Outputs saved:[/bold]")
        print(f"  • Code Audit: [cyan]{audit_file}[/cyan]")
        print(f"  • PRD: [cyan]{prd_file}[/cyan]")
        print(f"  • Deep Work Task: [cyan]{task_file}[/cyan]")

        print("\n:mag: [bold]Generated Code Audit Summary:[/bold]")
        print(f"  • Findings: {len(audit.findings)}")
        print(f"  • Severity: {audit.severity_overview.critical} critical, {audit.severity_overview.high} high")

        print("\n:page_facing_up: [bold]Generated PRD Summary:[/bold]")
        print(f"  • Product: {prd.product_name}")
        print(f"  • Status: {prd.status}")

        print("\n:dart: [bold]Generated Task Summary:[/bold]")

    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        traceback.print_exc()

@app.command("knowledge")
def cli_run_knowledge_flow(
    paper_file: Path = typer.Argument(..., exists=True, help="Path to the scientific paper."),
    triples_only: bool = typer.Option(False, "--triples-only", help="Only extract and save knowledge graph triples."),
    output_dir: Path = typer.Option(
        None, 
        "--output-dir", 
        help="The directory to save output files. Defaults to './cultivation/systems/PromptVerge/outputs'",
        writable=True,
        resolve_path=True
    )
):
    """Runs the full Paper -> KG -> Quiz knowledge workflow."""
    from .flows import knowledge_workflow

    try:
        print(f":scroll:  Reading paper from [bold cyan]{paper_file}[/bold cyan]")
        paper_content = paper_file.read_text()

        # Define output dir relative to the script file for robustness
        outputs_dir = output_dir or (Path(__file__).parent.parent / "outputs")
        outputs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if triples_only:
            print(":robot:  Executing knowledge extraction...")
            triples = knowledge_workflow.extract_kg_triples(paper_content)

            # The `extract_kg_triples` function already returns the triples as a list of string tuples.
            # No further processing is needed before saving to JSON.
            triples_for_json = triples

            output_path = outputs_dir / f"triples_{paper_file.stem}_{timestamp}.json"
            output_path.write_text(json.dumps(triples_for_json, indent=2))
            print(f":floppy_disk:  Knowledge triples saved to [bold green]{output_path}[/bold green]")
        else:
            # 1. Run the knowledge extraction and quiz generation workflow
            print(":robot:  Executing full knowledge workflow...")
            quiz = knowledge_workflow.run_knowledge_flow(paper_content)

            # 2. Save the generated quiz to a file
            output_path = outputs_dir / f"quiz_{paper_file.stem}_{timestamp}.json"
            output_path.write_text(quiz.model_dump_json(indent=2))

            # 3. Print a summary of the generated quiz
            print(":tada:  Quiz generated successfully!")
            print(f"  :floppy_disk:  Saved to [bold green]{output_path}[/bold green]")
            print(f"  • Questions: {len(quiz.questions)}")
            print(f"  • Status: {quiz.status}")
            print(f"  • Tags: {', '.join(quiz.tags)}")

    except Exception as e:
        print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        traceback.print_exc()

if __name__ == "__main__":
    app()
