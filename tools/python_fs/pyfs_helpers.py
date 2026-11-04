"""
Names available to the `!py` checks of the MCQ files in tools/python_fs/mcq/ (format: see tools/build_gate.py).

A check runs in the builder, with the question's right option as `ans`, all four as `opts` and the question text as `stem`.
These helpers run the Python program shown in the question with the verification interpreter, so an "output" answer key
is what the real interpreter printed, never what the author remembered.

    !py assert same(ans, stem)                 the right option is exactly what the program in the stem prints
    !py assert raises(stem) == ans             the program raises this exception (the option is its class name)
    !py assert ok(stem)                        the program runs without an error
"""
import re
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runner  # noqa: E402  (its imports are standard library only, so the builder's own Python can import it)

PYTHON = sys.executable   # the builder sets this to the verification interpreter
RUN = {"real": True}      # --no-run turns the checks into no-ops


def code_in(stem, language="python"):
    """The first fenced code block of the stem."""
    match = re.search(r"```" + language + r"[^\n]*\n(.*?)```", stem, re.S)
    assert match, f"no ```{language} block in the question"
    return match.group(1)


@lru_cache(maxsize=None)
def _run(code):
    return runner.run_in(PYTHON, code)


def _words(text):
    return " ".join(text.replace("`", " ").split())


def printed(stem):
    """What the program in the stem printed, as one string."""
    result = _run(code_in(stem))
    assert result["rc"] == 0, "the program in the question failed:\n" + result["err"]
    return result["out"].strip()


def same(answer, stem):
    """True when `answer` (backticks and spacing ignored) is what the program in the stem printed."""
    if not RUN["real"]:
        return True
    return _words(answer) == _words(printed(stem))


def raises(stem):
    """The name of the exception that ends the program in the stem (empty string when it ends normally)."""
    if not RUN["real"]:
        return ""
    result = _run(code_in(stem))
    if result["rc"] == 0:
        return ""
    last = result["err"].strip().splitlines()[-1]
    return last.split(":", 1)[0].strip()


def ok(stem):
    if not RUN["real"]:
        return True
    return _run(code_in(stem))["rc"] == 0
