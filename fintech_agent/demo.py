"""Demonstração real de três turnos; nunca produz evidência com serviços simulados."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import sys

from .runtime import AgentConfig, AgentContext, ClassificationUnavailable, ConfigurationError, build_agent, make_client, run_turn

DEMO_MESSAGES = (
    "I lost my bank card. How can I report it through the official support channel?",
    "When will my replacement card arrive?",
    "I made a bank transfer by mistake. How can I request its cancellation?",
)


async def run_demo(config: AgentConfig) -> dict:
    agent = build_agent(config.model)
    turns = []
    history = []
    async with make_client() as client:
        context = AgentContext(config, client)
        for text in DEMO_MESSAGES:
            result, events = await run_turn(agent, context, text, history)
            history = result.to_input_list()
            turns.append({"user": text, "assistant": str(result.final_output), "tool_events": events})
    intents = [next(event["classification"]["intent"] for event in turn["tool_events"] if event["status"] == "ok")
               for turn in turns]
    return {
        "execution": "real_openai_and_http_api",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "openai_agents_version": version("openai-agents"),
        "openai_version": version("openai"),
        "model": config.model,
        "task": "banking_intent_with_security",
        "tracing_disabled": True,
        "store": False,
        "messages": "synthetic_english_examples_not_evaluation_dataset",
        "observed_intents": intents,
        "distinct_intents_observed": len(set(intents)),
        "response_quality_review": "pending_manual_review",
        "turns": turns,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Arquivo JSON de evidência; escrito somente depois dos três turnos completos.")
    args = parser.parse_args()
    try:
        config = AgentConfig.from_environment()
        report = asyncio.run(run_demo(config))
    except (ConfigurationError, ClassificationUnavailable) as exc:
        print("Demonstração não concluída: " + str(exc), file=sys.stderr)
        return 2
    except Exception:
        # Exceções de provedores podem incluir o payload; não imprimir credenciais ou conteúdo.
        print("Demonstração não concluída: falha no provedor ou no ciclo do agente. Confira configuração, acesso ao modelo e disponibilidade da API.", file=sys.stderr)
        return 3
    content = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
        print("Evidência real gravada após três turnos completos.")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
