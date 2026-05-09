import shutil
import subprocess
from pathlib import Path
from fastapi import FastAPI, File, Form, Query, UploadFile

app = FastAPI()

PROJECT_DIR = Path("/home/aiserver/projects/can-log-summarizer")
PYTHON = PROJECT_DIR / ".venv/bin/python"
UPLOAD_DIR = PROJECT_DIR / "data/uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DBC = PROJECT_DIR / "data/dbcs/toyota.dbc"


def run_summarizer(dbc_path: Path, log_path: Path, model: str):
    """Run summarize_log.py as a subprocess and return its result."""
    cmd = [
        str(PYTHON),
        "src/summarize_log.py",
        str(dbc_path),
        str(log_path),
        model,
    ]
    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
        timeout=300,
    )
    return {
        "ok": result.returncode == 0,
        "model": model,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


@app.get("/summarize")
def summarize(
    dbc_path: str = Query(...),
    log_path: str = Query(...),
    model: str = Query("llama3.1:8b"),
):
    """Path-based endpoint. Useful for terminal/curl testing."""
    dbc = Path(dbc_path)
    log = Path(log_path)
    if not dbc.exists():
        return {"ok": False, "error": f"DBC file not found: {dbc}"}
    if not log.exists():
        return {"ok": False, "error": f"Log file not found: {log}"}
    return run_summarizer(dbc, log, model)


@app.post("/upload-and-summarize")
async def upload_and_summarize(
    file: UploadFile = File(...),
    dbc_path: str = Form(default=str(DEFAULT_DBC)),
    model: str = Form(default="llama3.1:8b"),
):
    """Upload-based endpoint. n8n posts the binary file directly here."""
    if not file.filename:
        return {"ok": False, "error": "No filename provided"}

    save_path = UPLOAD_DIR / file.filename
    with save_path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    dbc = Path(dbc_path)
    if not dbc.exists():
        return {
            "ok": False,
            "error": f"DBC file not found: {dbc}",
            "uploaded_to": str(save_path),
        }

    result = run_summarizer(dbc, save_path, model)
    result["uploaded_to"] = str(save_path)
    return result
