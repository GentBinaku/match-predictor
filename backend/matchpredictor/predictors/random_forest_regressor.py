from typing import List, Optional, Tuple

import joblib # type: ignore
import numpy as np
from numpy import float64
from numpy.typing import NDArray
from sklearn.ensemble import RandomForestRegressor # type: ignore
from sklearn.model_selection import GridSearchCV # type: ignore
from sklearn.preprocessing import OneHotEncoder # type: ignore

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


class RandomForestPredictor(Predictor):
    def __init__(
        self,
        model: RandomForestRegressor,
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

        home_importance = np.array(fixture.home_importance).reshape(-1, 1)
        away_importance = np.array(fixture.away_importance).reshape(-1, 1)
        home_spi = np.array(fixture.home_spi).reshape(-1, 1)
        away_spi = np.array(fixture.away_spi).reshape(-1, 1)
        home_xg = np.array(fixture.home_xg).reshape(-1, 1)
        away_xg = np.array(fixture.away_xg).reshape(-1, 1)
        home_nsxg = np.array(fixture.home_nsxg).reshape(-1, 1)
        away_nsxg = np.array(fixture.away_nsxg).reshape(-1, 1)

        x: NDArray[float64] = np.concatenate(
            [
                encoded_home_name,
                encoded_away_name,
                encoded_home_points,
                encoded_away_points,
                np.array(home_avg_goals).reshape(-1, 1),
                np.array(away_avg_goals).reshape(-1, 1),
                home_importance,
                away_importance,
                home_spi,
                away_spi,
                home_xg,
                away_xg,
                home_nsxg,
                away_nsxg,
            ],
            1,
        )
        pred = self.model.predict(x)
        home_goals_pred, away_goals_pred = pred[0]
        if home_goals_pred > away_goals_pred:
            return Prediction(outcome=Outcome.HOME)
        elif home_goals_pred < away_goals_pred:
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


def build_model(results: List[Result]) -> Tuple[RandomForestRegressor, OneHotEncoder]:
    home_names = np.array([r.fixture.home_team.name for r in results])
    away_names = np.array([r.fixture.away_team.name for r in results])
    home_goals = np.array([r.home_goals for r in results])
    away_goals = np.array([r.away_goals for r in results])
    home_importance = np.array([r.fixture.home_importance for r in results]).reshape(
        -1, 1
    )
    away_importance = np.array([r.fixture.away_importance for r in results]).reshape(
        -1, 1
    )
    home_spi = np.array([r.fixture.home_spi for r in results]).reshape(-1, 1)
    away_spi = np.array([r.fixture.away_spi for r in results]).reshape(-1, 1)
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

    home_xg = np.array([r.fixture.home_xg for r in results]).reshape(-1, 1)
    away_xg = np.array([r.fixture.away_xg for r in results]).reshape(-1, 1)
    home_nsxg = np.array([r.fixture.home_nsxg for r in results]).reshape(-1, 1)
    away_nsxg = np.array([r.fixture.away_nsxg for r in results]).reshape(-1, 1)

    x: NDArray[float64] = np.concatenate(
        [
            encoded_home_names,
            encoded_away_names,
            encoded_home_points,
            encoded_away_points,
            home_avg_goals.reshape(-1, 1),
            away_avg_goals.reshape(-1, 1),
            home_importance,
            away_importance,
            home_spi,
            away_spi,
            home_xg,
            away_xg,
            home_nsxg,
            away_nsxg,
        ],
        1,
    )

    y = np.column_stack((home_goals, away_goals))

    n_cores = joblib.cpu_count(only_physical_cores=True)


    # Define the parameter grid
    param_grid = {
        "n_estimators": [50, 100, 200],
        "max_depth": [None, 10, 20, 30],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
    }

    # Create a base model
    rf = RandomForestRegressor()

    # Instantiate the grid search model
    grid_search = GridSearchCV(
        estimator=rf, param_grid=param_grid, cv=3, n_jobs=n_cores, verbose=0
    )

    # Fit the grid search to the data
    grid_search.fit(x, y)

    # Get the best model
    model = grid_search.best_estimator_

    return model, team_encoding


def train_random_forest_predictor(results: List[Result]) -> Predictor:
    model, team_encoding = build_model(results)
    return RandomForestPredictor(model, team_encoding, results)
