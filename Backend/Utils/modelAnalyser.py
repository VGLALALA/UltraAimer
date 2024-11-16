from ultralytics import YOLO
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
import os

console = Console()

def scan_models(folder_path):
    model_files = [
        os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pt')
    ]
    return model_files

def display_model_selection(model_files):
    console.print(Panel("Select a YOLO model to analyze:", style="bold green"))
    
    for idx, model in enumerate(model_files):
        console.print(f"[{idx + 1}] {model}")

    choice = Prompt.ask(
        "Enter the number corresponding to the model", 
        choices=[str(i + 1) for i in range(len(model_files))],
        show_choices=False
    )
    return model_files[int(choice) - 1]

def analyze_yolov10_model(model_path):
    try:
        model = YOLO(model_path)
        nc = len(model.names)
        img_size = model.model.input_size if hasattr(model.model, "input_size") else "Unknown"
        class_names = model.names
        model_size = os.path.getsize(model_path) / (1024 * 1024)

        table = Table(title="YOLOv10 Model Analysis")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta", no_wrap=False)
        table.add_row("Model Path", model_path)
        table.add_row("Number of Classes", str(nc))
        table.add_row("Model Size (MB)", f"{model_size:.2f}")
        table.add_row("Input Image Size", str(img_size))

        console.print(table)

        console.print("\n[bold green]Class Names:[/bold green]")
        class_table = Table(title="Class Names")
        class_table.add_column("Index", style="cyan")
        class_table.add_column("Class Name", style="magenta")
        for idx, name in class_names.items():
            class_table.add_row(str(idx), name)
        console.print(class_table)

    except Exception as e:
        console.print(f"[bold red]Error analyzing the model:[/bold red] {e}")

if __name__ == "__main__":
    model_folder = Prompt.ask(
        "Enter the path to the folder containing YOLO models", 
        default=os.getcwd()
    )
    
    model_files = scan_models(model_folder)

    if not model_files:
        console.print("[bold red]No YOLO models (.pt) found in the specified folder![/bold red]")
    else:
        selected_model = display_model_selection(model_files)
        analyze_yolov10_model(selected_model)