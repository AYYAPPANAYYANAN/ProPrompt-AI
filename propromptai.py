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

__version__ = "6.0.0"

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

def generate_flawless_project(prompt: str, api_key: str, error_feedback: str = ""):
    """Zero-Tolerance Code Generation for perfect 1st attempts."""
    client = Groq(api_key=api_key)
    
    # THE ZERO-TOLERANCE PROMPT
    system_prompt = (
        "You are an elite Principal AI Architect. You must generate flawless, production-ready, multi-file software.\n"
        "ZERO-TOLERANCE RULES:\n"
        "1. NO PLACEHOLDERS: You are strictly forbidden from using '# TODO', 'pass', or '# implement logic here'. You MUST write the actual, complete mathematical and programmatic logic for every single function.\n"
        "2. NO HALLUCINATIONS: Only use official, stable methods for libraries like pandas, sklearn, and streamlit. Ensure exactly that all file imports match across your generated files (e.g., if you import from 'data_engine.py', that file must exist in your JSON).\n"
        "3. EXTREME DENSITY: Write exhaustive, complex code with deep error handling (try/except blocks), logging, and advanced UI/UX. Files must be highly detailed.\n"
        "4. JSON STRICTNESS: NEVER use Python triple quotes. Escape all strings. Output ONLY a valid JSON object mapping relative file paths to complete code strings. Do not add markdown outside the JSON."
    )
    
    user_content = f"Project Requirement: {prompt}"
    
    if error_feedback:
        user_content += f"\n\nCRITICAL FIX: The code failed with:\n{error_feedback}\nFix the logic and imports perfectly. No triple quotes."

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.1, # Extremely low temperature to prevent hallucinations
        max_tokens=8000, 
        response_format={"type": "json_object"}
    )
    
    raw_content = completion.choices[0].message.content.strip()
    json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    else:
        return json.loads(raw_content)

def process_natural_language(prompt: str):
    cmd = prompt.lower()
    db = load_db()

    if "set groq key" in cmd or "set api key" in cmd:
        key = prompt.split("key")[-1].strip()
        db["groq_api_key"] = key
        save_db(db)
        console.print("[bold green]✔ Groq API Key saved securely![/bold green]")
        return

    if cmd.startswith("code ") or cmd.startswith("build "):
        if not db.get("groq_api_key"):
            console.print("[bold red]Missing API Key![/bold red]")
            return
            
        project_name = "flawless_build_" + str(len(db["tasks"]) + 1)
        last_error = ""
        
        max_attempts = 15
        for attempt in range(1, max_attempts + 1):
            console.print(f"[bold magenta]⚡ Attempt {attempt}/{max_attempts}: Engineering flawless code...[/bold magenta]")
            
            try:
                project_files = generate_flawless_project(prompt, db["groq_api_key"], last_error)
                
                for file_path, file_code in project_files.items():
                    full_path = Path(project_name) / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(file_code, encoding="utf-8")
                    
                console.print(f"[green]✔ Architecture built in: {project_name}[/green]")
                
                req_file = Path(project_name) / "requirements.txt"
                if req_file.exists():
                    console.print("[dim]📦 Installing dependencies...[/dim]")
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"])

                entry = "app.py" if "app.py" in project_files else ("main.py" if "main.py" in project_files else list(project_files.keys())[0])
                entry_path = Path(project_name) / entry
                
                if "streamlit" in open(entry_path, encoding="utf-8").read().lower():
                    console.print(f"[bold yellow]🚀 Launching Flawless Web App...[/bold yellow]\n")
                    subprocess.run([sys.executable, "-m", "streamlit", "run", str(entry_path)])
                    return
                else:
                    console.print(f"[bold yellow]🚀 Running backend service...[/bold yellow]\n")
                    result = subprocess.run([sys.executable, str(entry_path)], capture_output=True, text=True)

                    if result.returncode == 0:
                        console.print(Panel(result.stdout, title="✔ Success Output", border_style="green"))
                        return 
                    else:
                        last_error = result.stderr
                        console.print(Panel(last_error, title="❌ Error Detected (Auto-fixing)", border_style="red"))
                        
            except Exception as e:
                last_error = str(e)
                console.print(f"[bold red]System Crash:[/bold red] {last_error}")

        console.print(f"[bold red]❌ Exhausted {max_attempts} attempts.[/bold red]")
        return

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

    console.print(f"[yellow]I heard:[/yellow] {prompt}")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, words: list[str] = typer.Argument(None)):
    if ctx.invoked_subcommand is not None: return
    if not words:
        console.print("[bold blue]Zero-Tolerance Architect Active.[/bold blue]")
        return
    process_natural_language(" ".join(words))

if __name__ == "__main__":
    app()