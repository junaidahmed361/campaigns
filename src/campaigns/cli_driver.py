from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CliDriverResponse:
    driver: str
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    provider_response: str
    auth_mode: str = "existing_cli_config"

    @property
    def usable(self) -> bool:
        return self.returncode == 0 and bool(self.provider_response.strip())

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["usable"] = self.usable
        return payload


class CliAuthDriver:
    """Runs local Claude/Codex CLIs through their existing auth configuration.

    AgentOS never receives API keys and never reads or writes auth files. The CLI
    process is the credential boundary.
    """

    def __init__(self, name: str, command: tuple[str, ...], timeout_seconds: int = 240):
        self.name = name
        self.command = command
        self.timeout_seconds = timeout_seconds

    def run(self, prompt: str, cwd: str | Path | None = None) -> CliDriverResponse:
        completed = subprocess.run(
            (*self.command, prompt),
            cwd=str(cwd) if cwd is not None else None,
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            env=os.environ.copy(),
        )
        provider_response = completed.stdout.strip() if completed.returncode == 0 else ""
        return CliDriverResponse(
            driver=self.name,
            command=self.command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            provider_response=provider_response,
        )


def claude_code_driver() -> CliAuthDriver:
    binary = shutil.which("claude") or "/opt/homebrew/bin/claude"
    return CliAuthDriver(
        "claude-code-cli",
        (
            binary,
            "-p",
            "--max-budget-usd",
            "0.25",
            "--permission-mode",
            "plan",
            "--output-format",
            "text",
        ),
    )


def codex_cli_driver() -> CliAuthDriver:
    binary = shutil.which("codex") or "/opt/homebrew/bin/codex"
    return CliAuthDriver(
        "codex-cli",
        (binary, "exec", "--sandbox", "read-only", "--ephemeral"),
    )


def custom_command_driver(command: str) -> CliAuthDriver:
    return CliAuthDriver("custom-cli-command", ("/bin/bash", "-lc", command + " -- "))


def resolve_cli_driver(name: str = "auto", command: str | None = None) -> CliAuthDriver:
    if command:
        return custom_command_driver(command)
    if name == "claude":
        return claude_code_driver()
    if name == "codex":
        return codex_cli_driver()
    if name != "auto":
        raise ValueError(f"unknown driver: {name}")
    codex = codex_cli_driver()
    if Path(codex.command[0]).exists():
        return codex
    return claude_code_driver()
