# run_system.py
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple, Optional


REPO_ROOT = Path(__file__).resolve().parent
LOG_DIR = REPO_ROOT / "logs"
PID_DIR = REPO_ROOT / ".pids"
PID_FILE = PID_DIR / "system_pids.json"


def ts() -> str:
    return time.strftime("%H:%M:%S")


def log(level: str, msg: str) -> None:
    print(f"{ts()} {level:<8} {msg}", flush=True)


def load_dotenv(dotenv_path: Path) -> Dict[str, str]:
    """Minimal .env loader: KEY=VALUE; ignores empty lines and # comments."""
    env: Dict[str, str] = {}
    if not dotenv_path.exists():
        return env

    for raw in dotenv_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k:
            env[k] = v
    return env


def which_or_fail(exe: str) -> None:
    if shutil.which(exe) is None:
        raise RuntimeError(f"Не найдено в PATH: {exe}")


def resolve_npm_executable() -> str:
    # On Windows, npm is usually npm.cmd; with shell=False it's safer.
    if os.name == "nt":
        return shutil.which("npm.cmd") or shutil.which("npm") or "npm.cmd"
    return shutil.which("npm") or "npm"


def open_log(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Open as a plain file handle for subprocess redirection
    return open(path, "a", encoding="utf-8", errors="replace")


def spawn_process(
    name: str,
    cmd: List[str],
    cwd: Path,
    env: Dict[str, str],
    log_path: Path,
) -> subprocess.Popen:
    out_f = open_log(log_path)

    popen_kwargs = dict(
        cwd=str(cwd),
        env=env,
        stdout=out_f,
        stderr=out_f,
    )

    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    try:
        proc = subprocess.Popen(cmd, **popen_kwargs)
    except OSError as e:
        raise RuntimeError(f"[{name}] Не удалось запустить: {cmd}. Ошибка: {e}") from e

    log("INFO", f"START {name:<12} pid={proc.pid} cmd={' '.join(cmd)}")
    return proc


def stop_pid_windows(pid: int) -> None:
    # /T = kill process tree, /F = force
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)


def stop_process(name: str, proc: subprocess.Popen, grace_s: float = 6.0) -> None:
    if proc.poll() is not None:
        return

    log("INFO", f"STOP  {name:<12} pid={proc.pid}")

    try:
        if os.name == "nt":
            # Try CTRL+BREAK first (works for process group)
            try:
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            except Exception:
                pass

            t0 = time.time()
            while time.time() - t0 < grace_s:
                if proc.poll() is not None:
                    return
                time.sleep(0.25)

            # Force kill tree
            stop_pid_windows(proc.pid)
        else:
            proc.terminate()
            t0 = time.time()
            while time.time() - t0 < grace_s:
                if proc.poll() is not None:
                    return
                time.sleep(0.25)
            proc.kill()
    except Exception:
        # Last resort
        try:
            if os.name == "nt":
                stop_pid_windows(proc.pid)
            else:
                proc.kill()
        except Exception:
            pass


def http_ok(url: str, timeout_s: float = 2.0) -> bool:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return 200 <= resp.status < 500
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return False


def wait_http(url: str, timeout_s: float, label: str) -> bool:
    log("INFO", f"Ожидаю {label} (timeout {int(timeout_s)}s): {url}")
    deadline = time.time() + timeout_s
    last_print = 0.0

    while time.time() < deadline:
        if http_ok(url):
            log("INFO", f"{label} OK")
            return True

        elapsed = int(timeout_s - (deadline - time.time()))
        if time.time() - last_print >= 3.0:
            log("INFO", f"...жду {label} ({elapsed}s)")
            last_print = time.time()

        time.sleep(1.0)

    log("WARNING", f"Таймаут ожидания {label} ({int(timeout_s)}s)")
    return False


def main() -> int:
    # Prereqs
    try:
        which_or_fail("node")
        npm_exe = resolve_npm_executable()
        if shutil.which(npm_exe) is None:
            which_or_fail("npm.cmd" if os.name == "nt" else "npm")
    except RuntimeError as e:
        log("ERROR", str(e))
        return 2

    py = sys.executable

    # Build base env ONCE (fixes UnboundLocalError)
    base_env: Dict[str, str] = dict(os.environ)

    # Load .env if present
    base_env.update(load_dotenv(REPO_ROOT / ".env"))

    # Force UTF-8 for ALL child Python processes (fixes UnicodeEncodeError on emoji)
    base_env["PYTHONUTF8"] = "1"
    base_env["PYTHONIOENCODING"] = "utf-8:replace"
    base_env["PYTHONUNBUFFERED"] = "1"

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    PID_DIR.mkdir(parents=True, exist_ok=True)

    # Agents: (name, script path, port)
    agents: List[Tuple[str, str, int]] = [
        ("fundamental", "agents/fundamental_analyst_server.py", 8001),
        ("technical", "agents/technical_analyst_server.py", 8002),
        ("news_sentiment", "agents/news_sentiment_analyst_server.py", 8003),
        ("macro", "agents/macro_analyst_server.py", 8004),
        ("regulatory", "agents/regulatory_analyst_server.py", 8005),
        ("predictor", "agents/predictor_agent_server.py", 8006),
    ]

    procs: Dict[str, subprocess.Popen] = {}

    def shutdown_all() -> None:
        for name, proc in list(procs.items())[::-1]:
            stop_process(name, proc)
        procs.clear()
        try:
            if PID_FILE.exists():
                PID_FILE.unlink()
        except Exception:
            pass

    def handle_signal(signum, frame) -> None:
        shutdown_all()
        raise SystemExit(0)

    try:
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
    except Exception:
        pass

    try:
        log("INFO", f"Repo: {REPO_ROOT}")

        # Step 0: frontend deps presence (informational only)
        node_modules = REPO_ROOT / "frontend" / "node_modules"
        if node_modules.exists():
            log("INFO", "STEP 0/3: frontend deps уже есть (node_modules)")
        else:
            log("INFO", "STEP 0/3: node_modules нет — возможно нужно npm install в frontend/")

        # Step 1: start agents
        log("INFO", "STEP 1/3: старт агентов")
        for name, rel_path, _port in agents:
            script = REPO_ROOT / rel_path
            if not script.exists():
                log("WARNING", f"[{name}] Не найден файл: {script}")
                continue
            procs[name] = spawn_process(
                name=name,
                cmd=[py, str(script)],
                cwd=REPO_ROOT,
                env=base_env,
                log_path=LOG_DIR / f"{name}.log",
            )

        # Wait agents (non-fatal timeouts; same behavior as твой лог)
        for name, _rel_path, port in agents:
            ok = wait_http(
                f"http://localhost:{port}/.well-known/agent-card.json",
                timeout_s=20.0,
                label=f"agent:{name}:{port}",
            )
            if not ok:
                log("WARNING", f"Агент {name} ({port}) не ответил вовремя — продолжаю")

        # Step 2: backend
        log("INFO", "STEP 2/3: старт backend (frontend_api.py -> :8000)")
        backend_path = REPO_ROOT / "frontend_api.py"
        if not backend_path.exists():
            log("ERROR", "Не найден frontend_api.py в корне репо.")
            shutdown_all()
            return 3

        procs["backend"] = spawn_process(
            name="backend",
            cmd=[py, str(backend_path)],
            cwd=REPO_ROOT,
            env=base_env,
            log_path=LOG_DIR / "backend.log",
        )

        ok_backend = wait_http(
            "http://localhost:8000/health",
            timeout_s=120.0,
            label="backend",
        )
        if not ok_backend:
            log("ERROR", "Backend не поднялся. См. logs/backend.log")
            shutdown_all()
            return 4

        # Step 3: frontend
        log("INFO", "STEP 3/3: старт frontend (Next.js dev -> :3001)")
        frontend_dir = REPO_ROOT / "frontend"
        if not frontend_dir.exists():
            log("ERROR", "Не найдена папка frontend/.")
            shutdown_all()
            return 5

        frontend_env = dict(base_env)
        frontend_env.setdefault("PORT", "3001")
        frontend_env.setdefault("NEXT_TELEMETRY_DISABLED", "1")

        procs["frontend"] = spawn_process(
            name="frontend",
            cmd=[resolve_npm_executable(), "run", "dev"],
            cwd=frontend_dir,
            env=frontend_env,
            log_path=LOG_DIR / "frontend.log",
        )

        wait_http("http://localhost:3001/", timeout_s=120.0, label="frontend")

        # Persist PIDs for stop script
        try:
            PID_FILE.write_text(
                json.dumps({k: v.pid for k, v in procs.items()}, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

        log("INFO", f"Frontend: http://localhost:3001")
        log("INFO", f"Backend:  http://localhost:8000")
        log("INFO", "Остановка: Ctrl+C (или Stop в IDE).")

        # Keep alive
        while True:
            # If backend or frontend dies -> stop all
            for critical in ("backend", "frontend"):
                p = procs.get(critical)
                if p and p.poll() is not None:
                    log("ERROR", f"[{critical}] завершился (code={p.returncode}). Останавливаю систему.")
                    shutdown_all()
                    return 6
            time.sleep(1.0)

    except KeyboardInterrupt:
        shutdown_all()
        return 0
    except SystemExit:
        shutdown_all()
        return 0
    except Exception as e:
        log("ERROR", f"Ошибка: {e}")
        shutdown_all()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
