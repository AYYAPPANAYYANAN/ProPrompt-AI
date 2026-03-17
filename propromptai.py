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

__version__ = "5.0.0"

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

def generate_ai_studio_project(prompt: str, api_key: str, error_feedback: str = ""):
    """Google AI Studio level generation with strict JSON safety."""
    client = Groq(api_key=api_key)
    
    system_prompt = (
        "You are an elite 'AI Studio' System Architect. Your job is to generate full, working applications, "
        "entire websites, and massive SaaS platforms from a single prompt. "
        "CRITICAL JSON & PYTHON RULES: "
        "1. NEVER USE TRIPLE QUOTES (\"\"\" or ''') inside the Python code. This breaks JSON parsing. Use standard single or double quotes with \\n for newlines. "
        "2. Ensure all strings inside the code are properly escaped to maintain valid JSON. "
        "3. DO NOT write short scripts. Write extensive, exhaustive, production-ready code exceeding hundreds of lines per file. "
        "4. NO placeholders like '# implementation here'. Write every single line of logic. "
        "5. Output ONLY a valid JSON object mapping relative file paths to complete code strings. "
        "Example: {'app.py': '...', 'components/ui.py': '...', 'requirements.txt': '...'}"
    )
    
    user_content = f"AI Studio Project Requirement: {prompt}"
    
    if error_feedback:
        user_content += f"\n\nCRITICAL FIX REQUIRED. The previous attempt crashed:\n{error_feedback}\nRewrite the JSON to fix this perfectly. REMEMBER: DO NOT use triple quotes."

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.3, 
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

    # ACTION 0: Setup Groq API Key
    if "set groq key" in cmd or "set api key" in cmd:
        key = prompt.split("key")[-1].strip()
        db["groq_api_key"] = key
        save_db(db)
        console.print("[bold green]✔ Groq API Key saved securely![/bold green]")
        return

    # ACTION 1: The AI Studio Auto-Builder
    if cmd.startswith("code ") or cmd.startswith("build "):
        if not db.get("groq_api_key"):
            console.print("[bold red]Missing API Key![/bold red]")
            return
            
        project_name = "ai_studio_build_" + str(len(db["tasks"]) + 1)
        last_error = ""
        
        # EXTENDED RETRY LOOP (15 Attempts for maximum auto-healing)
        max_attempts = 15
        for attempt in range(1, max_attempts + 1):
            console.print(f"[bold magenta]⚡ Attempt {attempt}/{max_attempts}: AI Studio is architecting...[/bold magenta]")
            
            try:
                project_files = generate_ai_studio_project(prompt, db["groq_api_key"], last_error)
                
                for file_path, file_code in project_files.items():
                    full_path = Path(project_name) / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(file_code, encoding="utf-8")
                    
                console.print(f"[green]✔ Website/App built in: {project_name}[/green]")
                
                req_file = Path(project_name) / "requirements.txt"
                if req_file.exists():
                    console.print("[dim]📦 Installing dependencies...[/dim]")
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"])

                entry = "app.py" if "app.py" in project_files else ("main.py" if "main.py" in project_files else list(project_files.keys())[0])
                entry_path = Path(project_name) / entry
                
                if "streamlit" in open(entry_path, encoding="utf-8").read().lower():
                    console.print(f"[bold yellow]🚀 Launching AI Studio Web App...[/bold yellow]\n")
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

        console.print(f"[bold red]❌ Exhausted {max_attempts} attempts. Check the code manually.[/bold red]")
        return

    # ACTION 2: Memory
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
        console.print("[bold blue]AI Studio Architect Active.[/bold blue]")
        return
    process_natural_language(" ".join(words))

if __name__ == "__main__":
    app()