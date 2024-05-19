from typing import List

from matchpredictor.matchresults.result import Fixture, Outcome, Result
from matchpredictor.predictors.predictor import Prediction, Predictor


class AlphabetPredictor(Predictor):
    def predict(self, fixture: Fixture) -> Prediction:
        # This predictors chooses
        # the first alphabetically listed team as
        # the winner
        return Prediction(
            outcome=(
                Outcome.HOME
                if fixture.home_team.name < fixture.away_team.name
                else Outcome.AWAY
            )
        )


def train_alphabet_predictor(results: List[Result]) -> Predictor:
    return AlphabetPredictor()
