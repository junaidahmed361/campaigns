from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from .compiler import CampaignCompiler
from .models import CampaignSpec, OrganizationBlueprint


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="campaigns", description="Compile campaign goals into accountable AgentRL-powered organizations.")
    sub = parser.add_subparsers(dest="command", required=True)
    compile_cmd = sub.add_parser("compile", help="Compile a campaign YAML file into a review dossier.")
    compile_cmd.add_argument("path", type=Path)
    compile_cmd.add_argument("--json", action="store_true", help="Emit JSON instead of YAML.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "compile":
        data = yaml.safe_load(args.path.read_text())
        campaign = CampaignSpec.from_dict(data)
        dossier = CampaignCompiler().compile(campaign, OrganizationBlueprint.default_for(campaign))
        payload = dossier.to_dict()
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(yaml.safe_dump(payload, sort_keys=False))
        return 0
    raise AssertionError(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
