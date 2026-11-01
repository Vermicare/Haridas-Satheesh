"""Offline guard for an operator-declared ESP32-S3 flash-ID command and output.

Does NOT run esptool, access a serial port, prove which command was run,
attest a device, or authorize any write. Deliberately supports only a narrow
read-only command grammar; unknown options fail closed.
"""
import json
import re
import shlex
import sys
from pathlib import Path


class CommandGuardError(ValueError):
    pass


SHELL_CONTROL = re.compile(r"[\n\r;&|<>`$@]")
PORT = re.compile(r"(?:COM[1-9][0-9]*|/dev/tty(?:USB|ACM)[0-9]+|/dev/cu\.[A-Za-z0-9._-]+)", re.I)
MUTATING_OUTPUT = re.compile(
    r"(?im)(?:\b(?:write[-_]flash|erase[-_]flash|erase[-_]region|burn[-_]efuse)\b|"
    r"^\s*(?:flash will be erased|writing at|wrote\s+\d+\s+bytes|erasing flash|"
    r"hash of data verified|compressed\s+\d+\s+bytes to))"
)


def validate_declared_command(command: str) -> dict:
    """Validate a *declaration*, not the execution provenance of a command."""
    if not isinstance(command, str) or not 1 <= len(command) <= 512 or SHELL_CONTROL.search(command):
        raise CommandGuardError("missing, oversized, or shell-controlled command")
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError as exc:
        raise CommandGuardError("unparseable command") from exc
    if tokens[:3] in (["python", "-m", "esptool"], ["py", "-m", "esptool"]):
        tokens = tokens[3:]
    elif tokens and tokens[0].lower() in ("esptool", "esptool.py"):
        tokens = tokens[1:]
    else:
        raise CommandGuardError("only esptool CLI entrypoints are accepted")
    if not tokens or tokens[-1] not in ("flash-id", "flash_id"):
        raise CommandGuardError("exactly one read-only flash-id subcommand required at end")
    args = tokens[:-1]
    seen = {}
    idx = 0
    while idx < len(args):
        flag = args[idx]
        if flag not in ("--chip", "-p", "--port", "-b", "--baud") or idx + 1 >= len(args):
            raise CommandGuardError("unknown, duplicated or incomplete command option")
        key = {"-p": "port", "--port": "port", "--chip": "chip", "-b": "baud", "--baud": "baud"}[flag]
        if key in seen:
            raise CommandGuardError("duplicate command option")
        seen[key] = args[idx + 1]
        idx += 2
    if seen.get("chip", "").lower() != "esp32s3":
        raise CommandGuardError("explicit esp32s3 chip selection required")
    if not PORT.fullmatch(seen.get("port", "")):
        raise CommandGuardError("explicit recognized local serial port required")
    if "baud" in seen and (not seen["baud"].isdigit() or not 9600 <= int(seen["baud"]) <= 1000000):
        raise CommandGuardError("invalid baudrate")
    return {
        "declared_command_class": "ESP32S3_FLASH_ID_READ_ONLY",
        "declared_command_grammar_accepted": True,
        "command_execution_attested": False,
        "port": "REDACTED",
        "flash_authorized": False,
    }


def assess(command: str, transcript: str, build_flash_mb: int) -> dict:
    """Reject mutation-like logs, then delegate size/chip parsing to v1.5."""
    command_record = validate_declared_command(command)
    if not isinstance(transcript, str) or MUTATING_OUTPUT.search(transcript):
        raise CommandGuardError("transcript contains a possible write/erase operation")
    from read_only_flash_probe_v15 import inspect_transcript, ProbeError
    try:
        parsed = inspect_transcript(transcript, build_flash_mb)
    except ProbeError as exc:
        raise CommandGuardError("existing v1.5 transcript gate rejected input: " + str(exc)) from exc
    return {
        **command_record,
        "transcript_gate": parsed["gate"],
        "claimed_chip_family": parsed["chip_family_claimed"],
        "claimed_flash_mb": parsed["observed_flash_mb_claimed"],
        "build_flash_mb_declared": parsed["build_flash_mb_declared"],
        "flash_size_comparison": parsed["flash_size_comparison"],
        "physical_device_attested": False,
        "actual_command_proven": False,
        "psram_physical_identity": "TBD",
        "physical_sensor_capture": "TBD",
        "limitations": "Operator can misdeclare command or edit transcript; no independent physical or execution provenance.",
    }


def main(argv):
    if len(argv) != 3:
        print("usage: flash_id_command_guard_v21.py DECLARED_COMMAND.txt PRIVATE_TRANSCRIPT.txt BUILD_FLASH_MB", file=sys.stderr)
        return 2
    try:
        command = Path(argv[0]).read_text(encoding="utf-8").strip()
        transcript = Path(argv[1]).read_text(encoding="utf-8")
        result = assess(command, transcript, int(argv[2]))
    except (OSError, UnicodeError, ValueError) as exc:
        # Do not echo user-controlled command/transcript/path, which can contain identifiers.
        print(json.dumps({"gate": "HOLD_UNVERIFIED", "flash_authorized": False,
                          "reason_type": type(exc).__name__}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
