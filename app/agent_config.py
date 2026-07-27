from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentHeuristics:
    """Project heuristics for the first demo; calibrate with real interviews."""

    normal_follow_up_minimum: int = 0
    normal_follow_up_maximum: int = 2
    complex_follow_up_maximum: int = 3
    maximum_visible_follow_ups: int = 4
    maximum_agent_rounds: int = 8
    maximum_tool_rounds: int = 6
    maximum_repeated_tool_signature: int = 2
    allow_analysis_with_nonblocking_uncertainties: bool = True


AGENT_HEURISTICS = AgentHeuristics()
