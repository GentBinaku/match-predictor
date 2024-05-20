from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


@dataclass(frozen=True)
class Team(object):
    name: str


@dataclass(frozen=True)
class Fixture(object):
    home_team: Team
    away_team: Team
    league: str
    home_importance: Optional[float] = None
    away_importance: Optional[float] = None
    home_spi: Optional[float] = None
    away_spi: Optional[float] = None
    home_xg: Optional[float] = None
    away_xg: Optional[float] = None
    home_nsxg: Optional[float] = None
    away_nsxg: Optional[float] = None


@dataclass(frozen=True)
class Scenario(object):
    minutes_elapsed: int
    home_goals: int
    away_goals: int


class Outcome(str, Enum):
    HOME = "home"
    AWAY = "away"
    DRAW = "draw"


@dataclass
class Result(object):
    fixture: Fixture
    outcome: Outcome
    home_goals: int
    away_goals: int
    goal_difference: int = field(init=False)
    season: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "goal_difference", self.home_goals - self.away_goals)
