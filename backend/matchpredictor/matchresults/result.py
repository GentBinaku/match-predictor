from dataclasses import dataclass, field
from enum import Enum


@dataclass(frozen=True)
class Team(object):
    name: str


@dataclass(frozen=True)
class Fixture(object):
    home_team: Team
    away_team: Team
    league: str
    home_importance: float
    away_importance: float
    home_spi: float
    away_spi: float
    home_xg: float
    away_xg: float
    home_nsxg: float
    away_nsxg: float


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

    def __post_init__(self):
        object.__setattr__(self, "goal_difference", self.home_goals - self.away_goals)
