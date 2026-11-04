"""
Runs the code samples of the Python Full Stack guides. It is executed BY THE VERIFICATION INTERPRETER (tools/python_fs/.venv),
not by the builder, so the samples see the same Python and libraries every time.

    python runner.py tasks.json            -> prints {"<task id>": result, ...} as JSON
    python runner.py --versions            -> prints the interpreter and library versions as JSON
    python runner.py --doctest file.txt    (internal) runs a pycon transcript

A task is {"id", "kind", "code", "timeout"?, "stable"?, "expect_fail"?}:

  syntax   ast.parse only: the snippet must be valid Python for this interpreter
  run      the code is written to main.py in a fresh temp folder and run. Result: ok, out (stdout), err (stderr).
           stable=true runs it a second time and fails when stdout differs (a sample whose output is shown must be deterministic).
           expect_fail=true wants a non-zero exit (a traceback demo): ok is True when it failed, and err holds the traceback.
  doctest  a ">>> " transcript, every answer compared exactly (ELLIPSIS is allowed)

Results are cached by (kind, code, interpreter version, library versions) in the temp folder, so an unchanged sample is not run again.
"""
import ast
import concurrent.futures
import doctest
import hashlib
import importlib.metadata as md
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CACHE_FILE = Path(tempfile.gettempdir()) / "pyfs-run-cache.json"
LIBS = ["fastapi", "starlette", "pydantic", "sqlalchemy", "alembic", "django", "djangorestframework", "flask", "redis", "fakeredis",
        "celery", "httpx", "pytest", "pytest-asyncio", "tenacity", "pyjwt", "pwdlib", "confluent-kafka", "mypy", "hypothesis", "uvicorn", "anyio"]


def versions():
    out = {"python": sys.version.split()[0]}
    for lib in LIBS:
        try:
            out[lib] = md.version(lib)
        except md.PackageNotFoundError:
            pass
    return out


RUNNER_VERSION = "3"   # part of the cache key: bump it when the cleaning below changes


def only_own_frames(text):
    """Keeps the traceback frames that belong to the sample (main.py) and replaces runs of library frames by one marker line,
    so a shown traceback never contains paths of the machine that built the page."""
    lines, out, i, skipped = text.split("\n"), [], 0, False
    while i < len(lines):
        line = lines[i]
        if line.startswith('  File "'):
            j = i + 1
            while j < len(lines) and lines[j].startswith("    "):
                j += 1
            if 'File "main.py"' in line:
                out.extend(lines[i:j])
                skipped = False
            elif not skipped:
                out.append("  ... (frames inside libraries omitted)")
                skipped = True
            i = j
        else:
            out.append(line)
            i += 1
    return "\n".join(out)


def clean(text, folder):
    """Make a traceback or output independent of where the sample ran."""
    text = text.replace("\r\n", "\n").replace(folder, ".")
    text = re.sub(r'File "[^"]*[\\/]main\.py"', 'File "main.py"', text)
    if "Traceback (most recent call last)" in text:
        text = only_own_frames(text)
    text = re.sub(r"0x[0-9a-fA-F]{6,}", "0x…", text)
    return text.rstrip("\n")


def sample_env():
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "VIRTUAL_ENV", "PYTHONDONTWRITEBYTECODE")}
    env.update(PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8", PYTHONUTF8="1", NO_COLOR="1", COLUMNS="100")
    return env


def run_in(python, code, timeout=60):
    """Runs a snippet with the given interpreter (the builder's MCQ checks use this) -> {"rc", "out", "err"}."""
    return run_once(code, "run", timeout, python=python)


def run_once(code, kind, timeout, python=None):
    python = python or sys.executable
    folder = tempfile.mkdtemp(prefix="pyfs-")
    try:
        if kind == "doctest":
            (Path(folder) / "transcript.txt").write_text(code, encoding="utf-8")
            cmd = [python, "-X", "utf8", str(Path(__file__).resolve()), "--doctest", "transcript.txt"]
        else:
            (Path(folder) / "main.py").write_text(code, encoding="utf-8")
            cmd = [python, "-X", "utf8", "main.py"]
        try:
            done = subprocess.run(cmd, cwd=folder, env=sample_env(), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"rc": -1, "out": "", "err": f"timed out after {timeout}s"}
        return {"rc": done.returncode, "out": clean(done.stdout, folder), "err": clean(done.stderr, folder)}
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def do_task(task, cache, stamp):
    kind, code = task["kind"], task["code"]
    if kind == "syntax":
        try:
            ast.parse(code)
            return {"ok": True, "out": "", "err": ""}
        except SyntaxError as e:
            return {"ok": False, "out": "", "err": f"SyntaxError: {e.msg} (line {e.lineno}): {(e.text or '').strip()}"}
    key = hashlib.sha256(json.dumps([kind, code, stamp, bool(task.get("stable")), bool(task.get("expect_fail"))]).encode()).hexdigest()
    if key in cache:
        return cache[key]
    timeout = task.get("timeout", 60)
    first = run_once(code, kind, timeout)
    expect_fail = task.get("expect_fail")
    ok = (first["rc"] != 0) if expect_fail else first["rc"] == 0
    result = {"ok": ok, "out": first["out"], "err": first["err"]}
    if ok and task.get("stable"):
        second = run_once(code, kind, timeout)
        same = (second["err"] == first["err"]) if expect_fail else (second["out"] == first["out"])
        if not same:
            result.update(ok=False, err="the output changes from run to run, so it cannot be shown as the output")
    if kind == "run" and not ok and not expect_fail:
        result["err"] = first["err"] or first["out"]
    if kind == "run" and expect_fail and not ok:
        result["err"] = "was expected to fail but exited with 0"
    if kind == "doctest" and not ok:
        result["err"] = first["out"] or first["err"]
    if ok or not expect_fail:
        cache[key] = result
    return result


def main_tasks(path):
    tasks = json.loads(Path(path).read_text(encoding="utf-8"))
    cache = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except ValueError:
            cache = {}
    stamp = json.dumps(versions(), sort_keys=True) + RUNNER_VERSION
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, (os.cpu_count() or 4))) as pool:
        results = list(pool.map(lambda t: do_task(t, cache, stamp), tasks))
    # keep the cache bounded; only successful samples are stored
    if len(cache) > 20000:
        cache = dict(list(cache.items())[-10000:])
    try:
        CACHE_FILE.write_text(json.dumps({k: v for k, v in cache.items() if v.get("ok")}), encoding="utf-8")
    except OSError:
        pass
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({t["id"]: r for t, r in zip(tasks, results)}, ensure_ascii=False))


def main_doctest(path):
    text = Path(path).read_text(encoding="utf-8")
    test = doctest.DocTestParser().get_doctest(text, {"__name__": "__main__"}, "transcript", path, 0)
    buffer = io.StringIO()
    runner = doctest.DocTestRunner(optionflags=doctest.ELLIPSIS, verbose=False)
    runner.run(test, out=buffer.write, clear_globs=True)
    failed = runner.failures
    if failed:
        sys.stdout.reconfigure(encoding="utf-8")
        print(buffer.getvalue())
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    if sys.argv[1] == "--versions":
        print(json.dumps(versions()))
    elif sys.argv[1] == "--doctest":
        main_doctest(sys.argv[2])
    else:
        main_tasks(sys.argv[1])
