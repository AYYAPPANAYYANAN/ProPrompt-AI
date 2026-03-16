code 
import typer
import sys
import os
import re
import json
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

try:
    from groq import Groq
except ImportError:
    print("Please run: pip install groq")
    sys.exit(1)

__version__ = "1.0.0"

app = typer.Typer(add_completion=False, invoke_without_command=True)
console = Console()
DB_FILE = Path.home() / ".my_ai_db.json"

def load_db():
    if not DB_FILE.exists():
        return {"tasks": [], "groq_api_key": ""}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_ai_code(prompt: str, api_key: str):
    """Sends the user's idea to Groq and gets pure Python code back instantly."""
    client = Groq(api_key=api_key)
    
    system_prompt = (
        "You are an expert Python developer. Write a complete, working Python script for the user's request. "
        "Return ONLY the raw python code. Do not include markdown formatting like ```python, do not explain the code. "
        "Just the raw code starting with imports."
    )
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile", # Excellent, fast model for coding
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1, # Keep temperature low for reliable code
        max_tokens=2048
    )
    
    code = completion.choices[0].message.content.strip()
    
    # Clean up any accidental markdown the AI might slip in
    if code.startswith("```python"):
        code = code[9:]
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
        
    return code.strip()

def process_natural_language(prompt: str):
    cmd = prompt.lower()
    db = load_db()

    # ACTION 0: Setup Groq API Key
    if "set groq key" in cmd or "set api key" in cmd:
        key = prompt.split("key")[-1].strip()
        db["groq_api_key"] = key
        save_db(db)
        console.print("[bold green]✔ Groq API Key saved securely to your local database![/bold green]")
        return

    # ACTION 1: The Autonomous AI Coder
    if cmd.startswith("code ") or cmd.startswith("build a project "):
        if not db.get("groq_api_key"):
            console.print("[bold red]Missing Groq API Key![/bold red] Run: [yellow]mytool set groq key YOUR_KEY_HERE[/yellow]")
            return
            
        console.print("[bold blue]⚡ Groq LPU is thinking and writing your code...[/bold blue]")
        
        try:
            # Generate the code using Groq
            generated_code = generate_ai_code(prompt, db["groq_api_key"])
            
            folder_name = "ai_project_" + str(len(db["tasks"]) + 1)
            os.makedirs(folder_name, exist_ok=True)
            
            file_path = os.path.join(folder_name, "main.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(generated_code)
                
            console.print(Panel(f"Code saved to: [cyan]{os.path.abspath(file_path)}[/cyan]", title="✔ Project Built", border_style="green"))
            console.print("[bold yellow]🚀 Running your new AI project now...[/bold yellow]\n")
            
            # Execute the generated code!
            result = subprocess.run([sys.executable, file_path], capture_output=True, text=True)
            
            # --- THE AUTO-HEALING LOGIC ---
            if result.returncode != 0 and "ModuleNotFoundError" in result.stderr:
                # Find out which library is missing
                missing_module = re.search(r"No module named '(.+?)'", result.stderr)
                if missing_module:
                    mod_name = missing_module.group(1)
                    console.print(f"[bold magenta]📦 Missing library detected: '{mod_name}'. Auto-installing now...[/bold magenta]")
                    
                    # Command the system to install it silently
                    subprocess.run([sys.executable, "-m", "pip", "install", mod_name, "--quiet"])
                    console.print(f"[bold green]✔ Installed {mod_name}! Restarting Agent...[/bold green]\n")
                    
                    # Try running the code one more time
                    result = subprocess.run([sys.executable, file_path], capture_output=True, text=True)

            # Final Output Evaluation
            if result.returncode == 0:
                console.print(Panel(result.stdout, title="Terminal Output", border_style="green"))
            else:
                console.print(Panel(result.stderr, title="Code Execution Error", border_style="red"))
                
        except Exception as e:
            console.print(f"[bold red]Agent crashed:[/bold red] {str(e)}")

    # ACTION 2: Simple File/Folder Creation
    file_match = re.search(r"(?:create|make)\s+(?:a\s+)?(?:file|folder|directory)\s+(?:named\s+)?(.+)", prompt)
    if file_match and "project" not in cmd:
        name = file_match.group(1).strip()
        if "folder" in cmd or "directory" in cmd:
            os.makedirs(name, exist_ok=True)
            console.print(f"[green]✔ Created Folder:[/green] {name}")
        else:
            with open(name, "w") as f: f.write("")
            console.print(f"[green]✔ Created File:[/green] {name}")
        return

    # ACTION 3: Memory & Tasks
    if any(word in cmd for word in ["remember", "add", "note", "show", "list"]):
        if "show" in cmd or "list" in cmd:
            if not db["tasks"]:
                console.print("[yellow]Memory is empty.[/yellow]")
                return
            table = Table(title="🧠 Your AI Memory")
            table.add_column("ID", style="cyan"); table.add_column("Task", style="magenta")
            for i, task in enumerate(db["tasks"], 1): table.add_row(str(i), task)
            console.print(table)
        else:
            task = cmd.split("to ", 1)[-1] if "to " in cmd else cmd
            db["tasks"].append(task)
            save_db(db)
            console.print(f"[cyan]✔ Saved:[/cyan] {task}")
        return

    console.print(f"[yellow]I heard:[/yellow] {prompt}\n[cyan]Try: 'code a python script that prints the fibonacci sequence'[/cyan]")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, words: list[str] = typer.Argument(None)):
    if ctx.invoked_subcommand is not None: return
    if not words:
        console.print("[bold blue]AI CLI is active.[/bold blue]")
        return
    process_natural_language(" ".join(words))

if __name__ == "__main__":
    app()