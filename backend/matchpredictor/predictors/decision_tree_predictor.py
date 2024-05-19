from typing import List, Optional, Tuple

import numpy as np
from numpy import float64
from numpy.typing import NDArray
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder

from matchpredictor.matchresults.result import Fixture, Outcome, Result, Team
from matchpredictor.predictors.past_results_predictor import calculate_table
from matchpredictor.predictors.predictor import Prediction, Predictor


def calculate_average_goals(results: List[Result], team: Team, n: int) -> float:
    matches = [
        r for r in results if r.fixture.home_team == team or r.fixture.away_team == team
    ][-n:]
    goals = [
        r.home_goals if r.fixture.home_team == team else r.away_goals for r in matches
    ]
    return sum(goals) / len(goals) if goals else 0


class DecisionTreePredictor(Predictor):
    def __init__(
        self,
        model: RandomForestClassifier,
        team_encoding: OneHotEncoder,
        results: List[Result],
    ) -> None:
        self.model = model
        self.team_encoding = team_encoding
        self.results = results
        self.points_table = calculate_table(results)

    def predict(self, fixture: Fixture) -> Prediction:
        encoded_home_name = self.__encode_team(fixture.home_team)
        encoded_away_name = self.__encode_team(fixture.away_team)
        if encoded_home_name is None:
            return Prediction(outcome=Outcome.AWAY)
        if encoded_away_name is None:
            return Prediction(outcome=Outcome.HOME)
        home_avg_goals = calculate_average_goals(self.results, fixture.home_team, 5)
        away_avg_goals = calculate_average_goals(self.results, fixture.away_team, 5)
        encoded_home_points: NDArray[float64] = np.array(
            self.points_table.points_for(fixture.home_team)
        ).reshape(-1, 1)
        encoded_away_points: NDArray[float64] = np.array(
            self.points_table.points_for(fixture.away_team)
        ).reshape(-1, 1)

        x: NDArray[float64] = np.concatenate(
            [
                encoded_home_name,
                encoded_away_name,
                encoded_home_points,
                encoded_away_points,
                np.array(home_avg_goals).reshape(-1, 1),
                np.array(away_avg_goals).reshape(-1, 1),
            ],
            1,
        )
        pred = self.model.predict(x)
        if pred > 0:
            return Prediction(outcome=Outcome.HOME)
        elif pred < 0:
            return Prediction(outcome=Outcome.AWAY)
        else:
            return Prediction(outcome=Outcome.DRAW)

    def __encode_team(self, team: Team) -> Optional[NDArray[float64]]:
        try:
            result: NDArray[float64] = self.team_encoding.transform(
                np.array(team.name).reshape(-1, 1)
            )
            return result
        except ValueError:
            return None


def build_model(results: List[Result]) -> Tuple[RandomForestClassifier, OneHotEncoder]:
    home_names = np.array([r.fixture.home_team.name for r in results])
    away_names = np.array([r.fixture.away_team.name for r in results])
    home_goals = np.array([r.home_goals for r in results])
    away_goals = np.array([r.away_goals for r in results])
    team_names = np.array(list(home_names) + list(away_names)).reshape(-1, 1)
    team_encoding = OneHotEncoder(sparse=False).fit(team_names)
    encoded_home_names = team_encoding.transform(home_names.reshape(-1, 1))
    encoded_away_names = team_encoding.transform(away_names.reshape(-1, 1))
    home_avg_goals = np.array(
        [calculate_average_goals(results, r.fixture.home_team, 5) for r in results]
    )
    away_avg_goals = np.array(
        [calculate_average_goals(results, r.fixture.away_team, 5) for r in results]
    )

    pointsTable = calculate_table(results)

    encoded_home_points = np.array(
        [pointsTable.points_for(r.fixture.home_team) for r in results]
    ).reshape(-1, 1)

    encoded_away_points = np.array(
        [pointsTable.points_for(r.fixture.away_team) for r in results]
    ).reshape(-1, 1)

    x: NDArray[float64] = np.concatenate(
        [
            encoded_home_names,
            encoded_away_names,
            encoded_home_points,
            encoded_away_points,
            home_avg_goals.reshape(-1, 1),
            away_avg_goals.reshape(-1, 1),
        ],
        1,
    )
    y = np.sign(home_goals - away_goals)
    model = RandomForestClassifier(n_estimators=100, max_depth=5, n_jobs=-1)
    model.fit(x, y)
    return model, team_encoding


def train_decision_tree_predictor(results: List[Result]) -> Predictor:
    model, team_encoding = build_model(results)
    return DecisionTreePredictor(model, team_encoding, results)
