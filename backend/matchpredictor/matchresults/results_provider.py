import csv
from typing import Callable, Dict, List, Optional, cast

import requests

from matchpredictor.matchresults.result import Fixture, Outcome, Result, Team


def training_results(
    csv_location: str,
    year: int,
    result_filter: Callable[[Result], bool] = lambda result: True,
) -> List[Result]:
    return load_results(csv_location, lambda r: result_filter(r) and r.season < year)


def validation_results(
    csv_location: str,
    year: int,
    result_filter: Callable[[Result], bool] = lambda result: True,
) -> List[Result]:
    return load_results(csv_location, lambda r: result_filter(r) and r.season == year)


def load_results(
    csv_location: str,
    result_filter: Callable[[Result], bool] = lambda result: True,
) -> List[Result]:
    def match_outcome(home_goals: int, away_goals: int) -> Outcome:
        if home_goals > away_goals:
            return Outcome.HOME
        if away_goals > home_goals:
            return Outcome.AWAY
        return Outcome.DRAW

    def result_from_row(row: Dict[str, str]) -> Optional[Result]:
        try:
            home_goals = int(row["score1"])
            away_goals = int(row["score2"])

            return Result(
                fixture=Fixture(
                    home_team=Team(row["team1"]),
                    away_team=Team(row["team2"]),
                    home_importance=float(row["importance1"]),
                    away_importance=float(row["importance2"]),
                    home_spi=float(row["spi1"]),
                    away_spi=float(row["spi2"]),
                    home_xg=float(row["xg1"]),
                    away_xg=float(row["xg2"]),
                    home_nsxg=float(row["nsxg1"]),
                    away_nsxg=float(row["nsxg2"]),
                    league=row["league"],
                ),
                outcome=match_outcome(home_goals, away_goals),
                home_goals=home_goals,
                away_goals=away_goals,
                season=int(row["season"]),
            )
        except (KeyError, ValueError):
            return None

    training_data = requests.get(csv_location).text

    rows = csv.DictReader(training_data.splitlines())
    results = filter(
        lambda r: type(r) is Result and result_filter(r), map(result_from_row, rows)
    )

    return cast(List[Result], list(results))
