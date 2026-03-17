import typer
import sys
import os
import re
import json
import time
import webbrowser
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

# --- SHIELDS UP: DEPENDENCY CHECK ---
try:
    from groq import Groq
    from e2b_code_interpreter import Sandbox
except ImportError:
    print("❌ Critical dependencies missing. Run: pip install groq e2b_code_interpreter rich typer")
    sys.exit(1)

__version__ = "7.5.0"
app = typer.Typer(add_completion=False, invoke_without_command=True)
console = Console()
DB_FILE = Path.home() / ".my_ai_db.json"

# --- DATABASE LOGIC ---
def load_db():
    if not DB_FILE.exists():
        return {"tasks": [], "groq_api_key": "", "e2b_api_key": "", "team_mode": True}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- THE "BRAIN" (GROQ ARCHITECT) ---
def generate_studio_project(prompt: str, api_key: str, error_feedback: str = ""):
    client = Groq(api_key=api_key)
    
    # ADVANCED LOGIC: This system prompt is the "Secret Sauce"
    system_prompt = (
        "You are a visionary Principal AI Engineer and Lead UI/UX Designer.\n"
        "1. ADVANCED AI LOGIC: When building AI models, use state-of-the-art libraries (PyTorch, Transformers, Scikit-Learn). Implement deep feature engineering, hyperparameter tuning, and cross-validation. DO NOT write basic models.\n"
        "2. TRENDING UI/UX: Design UIs that reflect 2026 design trends: Glassmorphism, Dark Mode by default, Neumorphism, and fluid animations. Use custom CSS in Streamlit to override default styling. Focus on micro-interactions and visual hierarchy.\n"
        "3. NO TRIPLE QUOTES: Never use \"\"\" or '''. Use single/double quotes with \\n.\n"
        "4. EXHAUSTIVE IMPLEMENTATION: No placeholders like '# implementation here'. Write thousands of lines if necessary.\n"
        "5. STRICT JSON: Output ONLY valid JSON: {'file_path': 'code', 'requirements.txt': 'libs'}"
    )
    
    user_content = f"Requirement: {prompt}"
    if error_feedback:
        user_content += (
            f"\n\n🚨 AGENTIC DEBUG LOOP INITIATED 🚨\n"
            f"The execution crashed with this Stack Trace:\n{error_feedback}\n\n"
            f"Analyze the root cause of this error. "
            f"Is it a missing dependency? A syntax error? An empty buffer? "
            f"Rewrite the entire JSON architecture to permanently resolve this issue."
        )
        
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
        temperature=0.2, # Lower for higher reliability
        max_tokens=8000,
        response_format={"type": "json_object"}
    )
    
    # Bulletproof JSON Extraction
    raw = completion.choices[0].message.content.strip()
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    return json.loads(json_match.group(0)) if json_match else json.loads(raw)

# --- THE "BODY" (CLOUD EXECUTION) ---
def deploy_to_cloud(project_files, e2b_key):
    with Sandbox(api_key=e2b_key) as sandbox:
        console.print("[cyan]☁️  Cloud Sandbox MicroVM Booted...[/cyan]")
        
        # 1. Transfer files
        for path, code in project_files.items():
            sandbox.files.write(path, code)
        
        # 2. Dependency Resolution
        if "requirements.txt" in project_files:
            console.print("[dim]📦 Installing Cloud dependencies (Pandas, Streamlit, etc.)...[/dim]")
            sandbox.commands.run("pip install -r requirements.txt")

        # 3. Dynamic Entry Point Detection
        entry = "app.py" if "app.py" in project_files else "main.py"
        is_web = "streamlit" in project_files.get("requirements.txt", "").lower()

        if is_web:
            # Run in background and expose URL
            sandbox.commands.run(f"nohup streamlit run {entry} --server.port 8501 &", background=True)
            time.sleep(3) # Wait for server spin-up
            hostname = sandbox.get_hostname(8501)
            return True, f"https://{hostname}", ""
        else:
            # Run CLI/Backend and capture output
            result = sandbox.commands.run(f"python {entry}")
            if result.error:
                return False, "", result.stderr
            return True, result.stdout, ""

# --- THE "HEART" (CLI LOGIC) ---
def process_natural_language(prompt: str):
    db = load_db()
    cmd = prompt.lower()

    # KEY SETUP
    if "set groq key" in cmd:
        db["groq_api_key"] = prompt.split("key")[-1].strip()
        save_db(db); console.print("[green]✔ Groq Key Saved.[/green]"); return
    
    if "set e2b key" in cmd:
        db["e2b_api_key"] = prompt.split("key")[-1].strip()
        save_db(db); console.print("[green]✔ E2B Cloud Key Saved.[/green]"); return

    # ARCHITECT TRIGGER
    if cmd.startswith("build ") or cmd.startswith("code "):
        if not db.get("e2b_api_key") or not db.get("groq_api_key"):
            console.print("[bold red]ERROR: API Keys not set! Use 'set groq/e2b key'.[/bold red]")
            return

        last_error = ""
        max_retries = 15 # UNLIMITED FEELING: Deep auto-healing
        
        for attempt in range(1, max_retries + 1):
            console.print(Panel(f"🚀 AI Studio Attempt {attempt}/{max_retries}", border_style="magenta"))
            
            try:
                # 1. Generation
                files = generate_studio_project(prompt, db["groq_api_key"], last_error)
                
                # 2. Cloud Deployment
                success, output, error = deploy_to_cloud(files, db["e2b_api_key"])
                
                if success:
                    if output.startswith("https://"):
                        console.print(Panel(f"🌍 [bold green]PROJECT LIVE AT:[/bold green]\n[cyan]{output}[/cyan]", 
                                            title="✔ Deployment Success", border_style="green"))
                        console.print("[dim]Opening Live Preview in your browser...[/dim]")
                        # Simulate Hot-Reloading by opening the cloud URL automatically
                        webbrowser.open(output) 
                    else:
                        console.print(Panel(output, title="✔ Execution Success", border_style="green"))
                        
                    # Record success in team memory
                    db["tasks"].append(f"Built: {prompt[:30]}... (Attempt {attempt})")
                    save_db(db)
                    return
                else:
                    last_error = error
                    console.print(f"[red]❌ Error in Cloud Code. Auto-fixing...[/red]")

            except Exception as e:
                last_error = str(e)
                console.print(f"[red]⚠ System Crash: {last_error}[/red]")

        console.print("[bold red]❌ Exhausted all 15 attempts. The project complexity might be too high for a single pass.[/bold red]")

    # MEMORY VIEW
    if "show" in cmd or "list" in cmd:
        table = Table(title="🧠 Team Project Memory")
        table.add_column("ID", style="cyan"); table.add_column("Build History", style="magenta")
        for i, task in enumerate(db["tasks"], 1): table.add_row(str(i), task)
        console.print(table)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, words: list[str] = typer.Argument(None)):
    if not words:
        console.print(Panel("[bold white]Angle Master Edition V7.5[/bold white]\n[dim]Cloud-Sandboxed AI Studio CLI[/dim]", border_style="blue"))
        return
    process_natural_language(" ".join(words))

if __name__ == "__main__":
    app()