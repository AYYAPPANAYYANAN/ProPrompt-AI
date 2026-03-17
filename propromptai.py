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

__version__ = "4.0.1"

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

def generate_ultra_project(prompt: str, api_key: str, error_feedback: str = ""):
    """Uses Groq to architect a massive, multi-file enterprise system with UI/UX focus."""
    client = Groq(api_key=api_key)
    
    # THE "ULTRA" SYSTEM PROMPT
    system_prompt = (
        "You are a Staff-Level Software Engineer and an Expert UI/UX Designer. "
        "Your job is to build massive, highly polished, production-ready applications. "
        "CRITICAL INSTRUCTIONS: "
        "1. DO NOT write short, basic scripts. You MUST write extensive, exhaustive code. "
        "2. DO NOT use placeholders like '# logic goes here'. Write every single line of the logic. "
        "3. Focus heavily on UI/UX. Use advanced frontend frameworks (like Streamlit or FastAPI). "
        "   If using Streamlit, inject custom CSS, use columns, metrics, tabs, interactive charts, and animations. "
        "4. Structure the app across multiple files for deep modularity. "
        "5. Output ONLY a valid JSON object mapping relative file paths to complete code strings. "
        "Example: {'app.py': '...', 'components/ui.py': '...', 'database/models.py': '...', 'requirements.txt': '...'}. "
        "Do not include markdown explanations outside the JSON."
    )
    
    user_content = f"Enterprise Project Requirement: {prompt}"
    
    if error_feedback:
        user_content += f"\n\nCRITICAL FIX REQUIRED. The previous code crashed with this error:\n{error_feedback}\nRewrite the necessary JSON files to fix this perfectly."

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.3, 
        max_tokens=8000, # Maxed out token limit for massive code generation
        response_format={"type": "json_object"}
    )
    
    raw_content = completion.choices[0].message.content.strip()
    
    # The Regex JSON Cleaner (Bulletproof against Markdown crashes)
    json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    else:
        return json.loads(raw_content)

def process_natural_language(prompt: str):
    cmd = prompt.lower()
    db = load_db()

    # ACTION 0: Setup Groq API Key
    if "set groq key" in cmd or "set api key" in cmd:
        key = prompt.split("key")[-1].strip()
        db["groq_api_key"] = key
        save_db(db)
        console.print("[bold green]✔ Groq API Key saved securely![/bold green]")
        return

    # ACTION 1: The Autonomous Enterprise Architect
    if cmd.startswith("code ") or cmd.startswith("build "):
        if not db.get("groq_api_key"):
            console.print("[bold red]Missing API Key![/bold red]")
            return
            
        project_name = "ultra_project_" + str(len(db["tasks"]) + 1)
        last_error = ""
        
        for attempt in range(1, 4):
            console.print(f"[bold magenta]⚡ Attempt {attempt}: Architecting Ultra System with UI/UX...[/bold magenta]")
            
            try:
                # Generates the massive JSON structure
                project_files = generate_ultra_project(prompt, db["groq_api_key"], last_error)
                
                # Builds the physical files
                for file_path, file_code in project_files.items():
                    full_path = Path(project_name) / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(file_code, encoding="utf-8")
                    
                console.print(f"[green]✔ Multi-file architecture built in: {project_name}[/green]")
                
                # Installs dependencies
                req_file = Path(project_name) / "requirements.txt"
                if req_file.exists():
                    console.print("[dim]📦 Installing heavy dependencies...[/dim]")
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"])

                # Finds the main file
                entry = "app.py" if "app.py" in project_files else ("main.py" if "main.py" in project_files else list(project_files.keys())[0])
                entry_path = Path(project_name) / entry
                
                # Windows Streamlit Fix: Uses sys.executable -m to avoid path errors
                if "streamlit" in open(entry_path, encoding="utf-8").read().lower():
                    console.print(f"[bold yellow]🚀 Launching High-End Streamlit UI...[/bold yellow]\n")
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

        console.print("[bold red]❌ Exhausted auto-fix attempts. Check the code manually.[/bold red]")
        return

    # ACTION 2: Memory & Simple Files
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
        console.print("[bold blue]Ultra Architect Active.[/bold blue]")
        return
    process_natural_language(" ".join(words))

if __name__ == "__main__":
    app()