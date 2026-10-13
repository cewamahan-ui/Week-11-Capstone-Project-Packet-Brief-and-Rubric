"""Call cost ledger (Week 7 reuse).

Every model or tool call is booked here so the demo can print an
honest running total. Stub-mode calls cost 0.00 USD; the ledger still
records them so the cost table in ``docs/cost_analysis.md`` has a
traceable source.
"""

from __future__ import annotations


class CostTracker:
    """Accumulates per-call cost in USD for the current run."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def record(self, label: str, api_calls: int = 0, cost_usd: float = 0.0) -> None:
        self.calls.append(
            {
                "label": label,
                "api_calls": int(api_calls),
                "cost_usd": round(float(cost_usd), 6),
                "mode": "stub" if cost_usd == 0 else "live",
            }
        )

    @property
    def total_api_calls(self) -> int:
        return sum(c["api_calls"] for c in self.calls)

    @property
    def total_cost_usd(self) -> float:
        return round(sum(c["cost_usd"] for c in self.calls), 6)

    def summary(self) -> dict:
        return {
            "entries": len(self.calls),
            "total_api_calls": self.total_api_calls,
            "total_cost_usd": self.total_cost_usd,
            "mode": "stub" if self.total_cost_usd == 0 else "mixed",
        }
