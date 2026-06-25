from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from .autorun import CampaignAutorun
from .compiler import CampaignCompiler
from .dogfood import AgentOSDogfoodRunner, OutcomeRequest
from .dogfood_exec import DogfoodExecutionRunner
from .models import CampaignSpec, OrganizationBlueprint


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="campaigns", description="Compile campaign goals into accountable AgentRL-powered organizations.")
    parser.add_argument("--version", action="version", version="campaigns 0.1.0")
    sub = parser.add_subparsers(dest="command", required=True)
    compile_cmd = sub.add_parser("compile", help="Compile a campaign YAML file into a review dossier.")
    compile_cmd.add_argument("path", type=Path)
    compile_cmd.add_argument("--json", action="store_true", help="Emit JSON instead of YAML.")
    autorun_cmd = sub.add_parser("autorun", help="Run a bounded Claude-style observe/plan/act/verify/review campaign loop.")
    autorun_cmd.add_argument("path", type=Path)
    autorun_cmd.add_argument("--loops", type=int, default=3)
    autorun_cmd.add_argument("--json", action="store_true", help="Emit JSON instead of YAML.")
    dogfood_cmd = sub.add_parser("dogfood", help="Dogfood AgentOS intake: goal, budget, constraints, and quality only.")
    dogfood_cmd.add_argument("--goal", required=True, help="Outcome the user wants accomplished; do not specify providers.")
    dogfood_cmd.add_argument("--budget", type=float, default=None, help="Budget in dollars.")
    dogfood_cmd.add_argument("--constraint", action="append", default=[], help="Constraint; may be repeated.")
    dogfood_cmd.add_argument("--quality", action="append", default=[], help="Quality requirement; may be repeated.")
    dogfood_cmd.add_argument("--sla", default=None, help="Optional SLA / time expectation.")
    dogfood_cmd.add_argument("--json", action="store_true", help="Emit JSON instead of YAML.")
    exec_cmd = sub.add_parser("dogfood-exec", help="Dogfood Resource Manager reservations through local Claude/Codex CLI auth.")
    exec_cmd.add_argument("--goal", required=True, help="Outcome the user wants accomplished; do not specify providers.")
    exec_cmd.add_argument("--budget", type=float, required=True, help="User-visible budget in dollars.")
    exec_cmd.add_argument("--reserve", type=float, default=2.5, help="Resource Manager USD reservation for this run.")
    exec_cmd.add_argument("--constraint", action="append", default=[], help="Constraint; may be repeated.")
    exec_cmd.add_argument("--quality", action="append", default=[], help="Quality requirement; may be repeated.")
    exec_cmd.add_argument("--sla", default=None, help="Optional SLA / time expectation.")
    exec_cmd.add_argument("--driver", choices=("auto", "claude", "codex"), default="auto", help="Developer override; normal users should omit this.")
    exec_cmd.add_argument("--driver-command", default=None, help="Developer/test override command. The prompt is appended as the final shell argument.")
    exec_cmd.add_argument("--json", action="store_true", help="Emit JSON instead of YAML.")
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
    if args.command == "autorun":
        data = yaml.safe_load(args.path.read_text())
        result = CampaignAutorun().fit(CampaignSpec.from_dict(data)).autorun(max_loops=args.loops)
        payload = result.to_dict()
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(yaml.safe_dump(payload, sort_keys=False))
        return 0
    if args.command == "dogfood":
        request = OutcomeRequest(
            goal=args.goal,
            budget_dollars=args.budget,
            constraints=tuple(args.constraint),
            quality_requirements=tuple(args.quality),
            sla=args.sla,
        )
        payload = AgentOSDogfoodRunner().run(request).to_dict()
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(yaml.safe_dump(payload, sort_keys=False))
        return 0
    if args.command == "dogfood-exec":
        request = OutcomeRequest(
            goal=args.goal,
            budget_dollars=args.budget,
            constraints=tuple(args.constraint),
            quality_requirements=tuple(args.quality),
            sla=args.sla,
        )
        result = DogfoodExecutionRunner().run(
            request,
            resource_limit_dollars=args.budget,
            reserve_dollars=args.reserve,
            driver=args.driver,
            driver_command=args.driver_command,
            cwd=Path.cwd(),
        )
        payload = result.to_dict()
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(yaml.safe_dump(payload, sort_keys=False))
        return 0
    raise AssertionError(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
