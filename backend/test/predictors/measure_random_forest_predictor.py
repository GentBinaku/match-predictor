from test.predictors import csv_location
from unittest import TestCase

from matchpredictor.evaluation.evaluator import Evaluator
from matchpredictor.matchresults.results_provider import (
    training_results,
    validation_results,
)
from matchpredictor.predictors.random_forest_regressor import (
    train_random_forest_predictor,
)


class TestLinearRegressionPredictor(TestCase):
    def test_accuracy(self) -> None:
        training_data = training_results(
            csv_location, 2023, result_filter=lambda result: result.season >= 2021
        )
        validation_data = validation_results(csv_location, 2023)
        predictor = train_random_forest_predictor(training_data)

        accuracy, _ = Evaluator(predictor).measure_accuracy(validation_data)

        print(accuracy)

        self.assertGreaterEqual(accuracy, 0.4)
