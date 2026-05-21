"""``repro`` command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import REPRO_VERSION
from .recorder import record, write_record, DEFAULT_TIMEOUT_S
from .verifier import verify
from .auditor import audit


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="repro",
        description="Reproducible evidence recorder — record, verify, audit command runs.",
    )
    p.add_argument("--version", action="version", version=f"repro {REPRO_VERSION}")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("record", help="Run a command and write a .repro.yaml")
    pr.add_argument(
        "--input", action="append", default=[], metavar="PATH",
        help="Declare a file the command depends on. Repeatable.",
    )
    pr.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT_S, metavar="SEC",
        help=f"Hard wall-clock cap in seconds (default: {DEFAULT_TIMEOUT_S}).",
    )
    pr.add_argument(
        "--output", "-o", required=True, metavar="FILE",
        help="Destination .repro.yaml path.",
    )
    pr.add_argument(
        "--capture", choices=("full", "hash"), default="full",
        help="Inline stdout/stderr (full) or store only sha256 (hash).",
    )
    pr.add_argument(
        "--cwd", default=".", metavar="DIR",
        help="Working directory for the command (default: .).",
    )
    pr.add_argument(
        "argv", nargs=argparse.REMAINDER,
        help="The command to run. Use -- to separate.",
    )

    pv = sub.add_parser("verify", help="Replay a recorded command and report drift")
    pv.add_argument("record_path", help="Path to a .repro.yaml")
    pv.add_argument(
        "--cwd", default=None, metavar="DIR",
        help="Override cwd from the record (default: use stored cwd).",
    )

    pa = sub.add_parser("audit", help="Scan a directory and summarize repro records")
    pa.add_argument("directory", help="Directory containing *.repro.yaml files")

    return p


def _cmd_record(args: argparse.Namespace) -> int:
    argv = list(args.argv)
    # argparse keeps the leading "--" if present; drop it so we get a clean argv.
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        print("repro record: no command given", file=sys.stderr)
        return 2
    try:
        rec = record(
            argv,
            cwd=args.cwd,
            inputs=[Path(p) for p in args.input],
            timeout_s=args.timeout,
            capture=args.capture,
        )
    except (FileNotFoundError, IsADirectoryError, NotADirectoryError, ValueError) as exc:
        print(f"repro record: {exc}", file=sys.stderr)
        return 2
    write_record(rec, Path(args.output))
    status = rec["result"]["status"]
    print(f"recorded {args.output} (status={status}, exit_code={rec['result']['exit_code']})")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    try:
        result = verify(args.record_path, cwd=args.cwd)
    except (FileNotFoundError, ValueError) as exc:
        print(f"repro verify: {exc}", file=sys.stderr)
        return 2
    if result.ok:
        print(f"OK — {args.record_path}")
        return 0
    print(f"DRIFT — {args.record_path}")
    for d in result.drifts:
        print(f"  {d}")
    return 1


def _cmd_audit(args: argparse.Namespace) -> int:
    try:
        report = audit(args.directory)
    except NotADirectoryError as exc:
        print(f"repro audit: {exc}", file=sys.stderr)
        return 2
    print(f"audited {report.total} record(s):")
    print(f"  ok:              {report.ok_count}")
    print(f"  error:           {report.error_count}")
    print(f"  timeout:         {report.timeout_count}")
    print(f"  missing_command: {report.missing_command_count}")
    print(f"  dirty_git:       {report.dirty_git_count}")
    print(f"  schema_invalid:  {report.schema_invalid_count}")
    for e in report.entries:
        if e.issues:
            print(f"  {e.path}: {'; '.join(e.issues)}")
    return 0


def main(raw_argv: list[str] | None = None) -> int:
    p = _parser()
    args = p.parse_args(raw_argv)
    if args.cmd == "record":
        return _cmd_record(args)
    if args.cmd == "verify":
        return _cmd_verify(args)
    if args.cmd == "audit":
        return _cmd_audit(args)
    p.error(f"unknown subcommand {args.cmd!r}")
    return 2  # unreachable


if __name__ == "__main__":
    sys.exit(main())
