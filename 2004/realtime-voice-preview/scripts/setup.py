#!/usr/bin/env python3
"""One-shot setup for the Realtime Voice Preview skill.

Behaviour:
1. Copies the bundled ``template/`` directory to the project destination
   (default: ``/data/workspace/output/projects/realtime-voice-preview/``).
   - If the destination does not exist, it is created.
   - If it exists, files are updated in place while PRESERVING ``.env``.
     ``.env.example`` and ``.gitignore`` are always written so the user can
     discover fresh configuration.
   - ``--force`` replaces every bundled source/docs/manifest file but
     **never** overwrites a real ``.env`` (which contains a secret key).
2. Verifies that:
   - ``OPENAI_REALTIME_API_KEY`` is configured (clearly reports when missing,
     never prints any substring of the key).
   - The Starchild runtime at ``STARCHILD_RUNTIME_URL`` (default
     ``http://127.0.0.1:8000``) responds on ``/health``.
   - ``node`` is on ``PATH``.
   - The 59-case parser test suite passes.
   - The 16-case background-jobs test suite passes.

Run::

    python3 skills/realtime-voice-preview/scripts/setup.py
    python3 skills/realtime-voice-preview/scripts/setup.py --target /some/other/dir
    python3 skills/realtime-voice-preview/scripts/setup.py --force

Exit code 0 only when every check passes; non-zero otherwise.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.request import urlopen

# --------------------------------------------------------------------------- #
# Paths and constants
# --------------------------------------------------------------------------- #
WORKSPACE = Path(os.environ.get("STARCHILD_WORKSPACE", "/data/workspace"))
SKILL_ROOT = Path(__file__).resolve().parent.parent
BUNDLED_TEMPLATE = SKILL_ROOT / "template"
DEFAULT_TARGET = WORKSPACE / "output" / "projects" / "realtime-voice-preview"
WORKSPACE_ENV_FILE = WORKSPACE / ".env"

# Files that are part of the bundled template. All paths are relative to the
# template root. ``.env`` is intentionally ABSENT - the user's secret must
# survive every setup run, including --force.
BUNDLED_FILES = (
    "project.yaml",
    "PROJECT.md",
    "ANALYSIS.md",
    ".env.example",
    ".gitignore",
    "src/server.py",
    "src/index.html",
    "src/parser.js",
    "src/README.md",
    "src/smoke.py",
    "src/test_function_calls.js",
    "src/test_background_jobs.py",
)

PARSER_TEST_EXPECTED = 59
BG_TEST_EXPECTED = 16

# --------------------------------------------------------------------------- #
# Terminal colours
# --------------------------------------------------------------------------- #
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
DIM = "\033[2m"
RESET = "\033[0m"


# --------------------------------------------------------------------------- #
# Tiny output helpers
# --------------------------------------------------------------------------- #
class Report:
    """Accumulates check results so we can print a single summary at the end."""

    def __init__(self):
        self._rows = []

    def add(self, name, ok, detail=""):
        marker = f"{GREEN}OK{RESET}" if ok else f"{RED}BAD{RESET}"
        line = f"  {marker} {name}"
        if detail:
            line += f" - {detail}"
        self._rows.append((ok, line))
        print(line)

    def note(self, line):
        print(f"  {YELLOW}NOTE{RESET} {line}")

    @property
    def failed_names(self):
        return [name for ok, name in self._rows if not ok]

    @property
    def all_ok(self):
        return bool(self._rows) and all(ok for ok, _ in self._rows)


# --------------------------------------------------------------------------- #
# Secret-handling helpers - must never print any key substring
# --------------------------------------------------------------------------- #
def _parse_env_text(text):
    """Parse a minimal subset of .env syntax: KEY=value lines, # comments."""
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip()
        # Strip a single matched pair of wrapping quotes.
        if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
            v = v[1:-1]
        if k:
            out[k] = v
    return out


def _global_env_key():
    """Return (key, source-label) from shell env + workspace .env."""
    for var in ("OPENAI_REALTIME_API_KEY", "OPENAI_API_KEY"):
        val = os.environ.get(var)
        if val:
            return val, f"env:{var}"
    if WORKSPACE_ENV_FILE.exists():
        try:
            data = _parse_env_text(WORKSPACE_ENV_FILE.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            data = {}
        for k in ("OPENAI_REALTIME_API_KEY", "OPENAI_API_KEY"):
            if data.get(k):
                return data[k], f"envfile:{k}"
    return None, ""


def _project_env_key(target):
    """Look in project-local .env files (cwd first, then <target>).

    The .env inside the project target is never written by setup.py - if
    it is present it means the user placed it there and we should respect it.
    """
    for candidate in (Path.cwd() / ".env", target / ".env"):
        try:
            if not candidate.exists():
                continue
            data = _parse_env_text(candidate.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        for k in ("OPENAI_REALTIME_API_KEY", "OPENAI_API_KEY"):
            if data.get(k):
                return data[k], str(candidate)
    return None, ""


def _fingerprint(val, src):
    """Report only where a key was found; never reveal any key characters."""
    safe_src = src if src else "secure environment"
    return f"configured ({safe_src})"


def key_status(target):
    """Return (display-label, present?, detail) considering project-local .env."""
    val, src = _project_env_key(target)
    if val:
        return "present", True, _fingerprint(val, src)
    val, src = _global_env_key()
    if val:
        return "present", True, _fingerprint(val, src)
    return "missing", False, (
        "MISSING - call request_env_input for OPENAI_REALTIME_API_KEY (never "
        "ask in chat). Get a key at https://platform.openai.com/api-keys, "
        "enable project billing/credits, ensure Realtime model access, and "
        "prefer a narrowly-scoped project-scoped key (no org:read, no extra "
        "product scopes)."
    )


# --------------------------------------------------------------------------- #
# Copy / sync the bundled template
# --------------------------------------------------------------------------- #
def _iter_bundled(template):
    for rel in BUNDLED_FILES:
        src = template / rel
        if not src.exists():
            continue
        yield src, src.relative_to(template)


def copy_template(template, target, force):
    """Copy the bundled template to ``target``.

    Honours the rules in the module docstring: ``.env`` is never written by
    this function, even when ``force`` is set. Returns ``(actions, dest_existed)``.
    """
    if not template.is_dir():
        raise FileNotFoundError(f"bundled template missing: {template}")

    existed = target.exists()
    target.mkdir(parents=True, exist_ok=True)
    actions = []
    for src, rel in _iter_bundled(template):
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Rule: never overwrite .env. Belt-and-braces in case a future edit
        # accidentally adds the secret file to BUNDLED_FILES.
        if rel.name == ".env":
            actions.append(f"skipped {rel.as_posix()} (secret)")
            continue

        if dest.exists() and not force:
            shutil.copy2(src, dest)
            actions.append(f"updated {rel.as_posix()}")
        else:
            action = "replaced" if dest.exists() else "wrote"
            shutil.copy2(src, dest)
            actions.append(f"{action} {rel.as_posix()}")
    return actions, existed


# --------------------------------------------------------------------------- #
# Verifications
# --------------------------------------------------------------------------- #
def check_api_key(target, report):
    label, ok, detail = key_status(target)
    report.add(f"OPENAI_REALTIME_API_KEY ({label})", ok, detail)
    return ok


def check_runtime(report):
    runtime_url = os.environ.get("STARCHILD_RUNTIME_URL", "http://127.0.0.1:8000")
    try:
        with urlopen(f"{runtime_url}/health", timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        ok = bool(data.get("status") == "ok")
        report.add(
            "Starchild runtime /health",
            ok,
            f"reachable at {runtime_url}" if ok else f"unhealthy at {runtime_url}: {data!r}",
        )
        return ok
    except (URLError, TimeoutError, ConnectionError, OSError, ValueError) as e:
        report.add(
            "Starchild runtime /health",
            False,
            f"unreachable at {runtime_url}: {type(e).__name__}",
        )
        return False


def check_node(report):
    node = shutil.which("node")
    if not node:
        report.add("Node.js", False, "not found on PATH - parser tests will be skipped")
        return False
    try:
        r = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=5)
        ver = (r.stdout or r.stderr).strip()
    except Exception as e:
        report.add("Node.js", False, f"version probe failed: {e!s:.60}")
        return False
    report.add("Node.js", True, f"{node} ({ver})")
    return True


def check_files(target, report):
    missing = [rel for rel in BUNDLED_FILES if not (target / rel).exists()]
    report.add(
        "Template files",
        not missing,
        f"all {len(BUNDLED_FILES)} files present"
        if not missing
        else f"missing: {', '.join(missing)}",
    )
    return not missing


def _run(cmd, cwd, *, timeout=60):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)


def check_parser_tests(target, report, node_ok):
    if not node_ok:
        report.note(f"Parser tests skipped (Node.js unavailable).")
        return False
    node = shutil.which("node") or "node"
    test_file = target / "src" / "test_function_calls.js"
    if not test_file.exists():
        report.add(f"Parser tests ({PARSER_TEST_EXPECTED})", False, "test file missing")
        return False
    try:
        r = _run([node, str(test_file)], cwd=target)
    except subprocess.TimeoutExpired:
        report.add(f"Parser tests ({PARSER_TEST_EXPECTED})", False, "timed out")
        return False
    except Exception as e:
        report.add(
            f"Parser tests ({PARSER_TEST_EXPECTED})",
            False,
            f"failed to run: {type(e).__name__}",
        )
        return False
    ok = r.returncode == 0 and f"PASS: {PARSER_TEST_EXPECTED}" in r.stdout
    detail = (
        f"PASS: {PARSER_TEST_EXPECTED}/{PARSER_TEST_EXPECTED}"
        if ok
        else f"exit={r.returncode}; tail: {(r.stdout or r.stderr).strip()[-200:]}"
    )
    report.add(f"Parser tests ({PARSER_TEST_EXPECTED})", ok, detail)
    return ok


def check_background_tests(target, report):
    test_file = target / "src" / "test_background_jobs.py"
    if not test_file.exists():
        report.add(f"Background tests ({BG_TEST_EXPECTED})", False, "test file missing")
        return False
    try:
        r = subprocess.run(
            [sys.executable, "-m", "unittest", "test_background_jobs", "-v"],
            cwd=str(target / "src"),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        report.add(f"Background tests ({BG_TEST_EXPECTED})", False, "timed out")
        return False
    except Exception as e:
        report.add(
            f"Background tests ({BG_TEST_EXPECTED})",
            False,
            f"failed to run: {type(e).__name__}",
        )
        return False
    combined = (r.stdout or "") + "\n" + (r.stderr or "")
    ok = (
        r.returncode == 0
        and f"Ran {BG_TEST_EXPECTED} tests" in combined
        and "OK" in combined
    )
    detail = (
        f"{BG_TEST_EXPECTED}/{BG_TEST_EXPECTED} pass"
        if ok
        else f"exit={r.returncode}; tail: {combined.strip()[-200:]}"
    )
    report.add(f"Background tests ({BG_TEST_EXPECTED})", ok, detail)
    return ok


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
def parse_args(argv):
    p = argparse.ArgumentParser(
        prog="setup.py",
        description="Set up and verify the OpenAI Realtime Voice Preview project.",
    )
    p.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help=f"Destination project directory (default: {DEFAULT_TARGET})",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help=(
            "Replace bundled source/docs/manifest files in the target. "
            "NEVER overwrites .env (the secret key)."
        ),
    )
    p.add_argument(
        "--skip-copy",
        action="store_true",
        help="Do not copy the template; only run the verification checks.",
    )
    p.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip the parser and background-jobs test suites.",
    )
    p.add_argument(
        "--template",
        type=Path,
        default=BUNDLED_TEMPLATE,
        help=f"Bundled template directory (default: {BUNDLED_TEMPLATE})",
    )
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    target = args.target.resolve()
    template = args.template.resolve()
    report = Report()

    print("Realtime Voice Preview - Setup Check")
    print(f"  {DIM}target:   {target}{RESET}")
    print(f"  {DIM}template: {template}{RESET}")
    print()

    # --- Copy the template ------------------------------------------------- #
    if not args.skip_copy:
        try:
            actions, dest_existed = copy_template(template, target, force=args.force)
        except FileNotFoundError as e:
            report.add("Template copy", False, str(e))
            actions = []
            dest_existed = False
        else:
            verb = "force-replaced" if args.force else ("created" if not dest_existed else "synced")
            report.add(
                "Template copy",
                True,
                f"{verb} {len(actions)} bundled file(s); .env preserved",
            )

    # --- File presence ----------------------------------------------------- #
    if not args.skip_copy:
        check_files(target, report)

    # --- API key ---------------------------------------------------------- #
    # Check the project-local .env first, then the global env. The "missing"
    # message itself points the user at request_env_input rather than chat.
    key_ok = check_api_key(target, report)

    # --- Starchild runtime health ----------------------------------------- #
    runtime_ok = check_runtime(report)

    # --- Node availability ------------------------------------------------ #
    node_ok = check_node(report)

    # --- Tests ------------------------------------------------------------ #
    if not args.skip_tests:
        check_files(target, report)  # safety net when --skip-copy was used
        check_parser_tests(target, report, node_ok)
        check_background_tests(target, report)
    else:
        report.note("Tests skipped (--skip-tests).")

    # --- Summary ---------------------------------------------------------- #
    print()
    print("=" * 60)
    if report.all_ok:
        print(f"{GREEN}Ready to serve.{RESET}")
        print()
        print("Next steps:")
        print(f"  1. Start the demo server:")
        print(f"       python3 {target / 'src' / 'server.py'}")
        print(f"  2. Serve with the Preview tool using exactly:")
        print(f"       title    = 'OpenAI Realtime Voice Demo'")
        print(f"       dir      = 'output/projects/realtime-voice-preview/src'")
        print(f"       command  = 'python3 server.py'")
        print(f"       port     = 8765")
        print(f"  3. Verify health:  curl -sS http://127.0.0.1:8765/health")
        print(f"  4. Open the Preview URL in a SEPARATE full-screen tab")
        print(f"     (the embedded iframe cannot capture your microphone).")
        return 0

    failed = report.failed_names
    print(f"{RED}Not ready - fix {len(failed)} issue(s) above.{RESET}")
    if not key_ok:
        print(
            f"{YELLOW}Tip:{RESET} OPENAI_REALTIME_API_KEY is the most common "
            "miss. Call request_env_input (never ask in chat). If missing, "
            "obtain a key at https://platform.openai.com/api-keys, enable "
            "project billing/credits and ensure Realtime model access."
        )
    if not runtime_ok:
        print(
            f"{YELLOW}Tip:{RESET} Starchild runtime not reachable. Start it, "
            "or set STARCHILD_RUNTIME_URL to a reachable base URL."
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
