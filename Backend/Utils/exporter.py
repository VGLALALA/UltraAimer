import os
from ultralytics import YOLO
import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer()

def list_models(directory: str):
    """Lists available models in the specified directory."""
    return [f for f in os.listdir(directory) if f.endswith(".pt")]

@app.command()
def export_model():
    """
    Terminal UI for selecting and exporting a YOLO model.
    """
    # Step 1: Ask for the model folder path
    model_folder = typer.prompt("Enter the path to the folder containing YOLO models")

    # Validate the folder path
    if not os.path.isdir(model_folder):
        console.print(f"[red]The folder '{model_folder}' does not exist or is not accessible.[/red]")
        raise typer.Exit()

    # Step 2: Scan for models in the folder
    console.print(f"[bold green]Scanning for models in: {model_folder}[/bold green]")
    models = list_models(model_folder)

    if not models:
        console.print("[red]No YOLO models found in the specified folder.[/red]")
        raise typer.Exit()

    # Display models in a table
    table = Table(title="Available Models")
    table.add_column("Index", justify="center", style="cyan", no_wrap=True)
    table.add_column("Model Name", style="magenta")

    for i, model in enumerate(models):
        table.add_row(str(i), model)

    console.print(table)

    # Step 3: Ask the user to select a model
    model_index = typer.prompt("Enter the index of the model to export", type=int)

    if model_index < 0 or model_index >= len(models):
        console.print("[red]Invalid index selected![/red]")
        raise typer.Exit()

    selected_model = models[model_index]
    console.print(f"[bold green]Selected Model:[/bold green] {selected_model}")

    # Step 4: Display export options
    formats = ["onnx", "torchscript", "coreml", "tflite", "paddle", "engine"]
    table = Table(title="Export Formats")
    table.add_column("Index", justify="center", style="cyan", no_wrap=True)
    table.add_column("Format", style="magenta")

    for i, fmt in enumerate(formats):
        table.add_row(str(i), fmt)

    console.print(table)

    # Step 5: Ask the user to select an export format
    format_index = typer.prompt("Enter the index of the format to export to", type=int)

    if format_index < 0 or format_index >= len(formats):
        console.print("[red]Invalid index selected![/red]")
        raise typer.Exit()

    selected_format = formats[format_index]
    console.print(f"[bold green]Selected Format:[/bold green] {selected_format}")

    # Step 6: Export the selected model
    model_path = os.path.join(model_folder, selected_model)
    console.print(f"[bold blue]Exporting {selected_model} to {selected_format} format...[/bold blue]")

    try:
        model = YOLO(model_path)
        model.export(format=selected_format)
        console.print(f"[bold green]Model exported successfully to {selected_format} format![/bold green]")
    except Exception as e:
        console.print(f"[red]Failed to export model: {e}[/red]")

if __name__ == "__main__":
    app()
