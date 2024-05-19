from test.predictors import csv_location
from unittest import TestCase

from matchpredictor.evaluation.evaluator import Evaluator
from matchpredictor.matchresults.results_provider import (
    training_results,
    validation_results,
)
from matchpredictor.predictors.decision_tree_predictor import (
    train_decision_tree_predictor,
)


class TestLinearRegressionPredictor(TestCase):
    def test_accuracy(self) -> None:
        training_data = training_results(
            csv_location, 2021, result_filter=lambda result: result.season >= 2015
        )
        validation_data = validation_results(csv_location, 2021)
        predictor = train_decision_tree_predictor(training_data)

        accuracy, _ = Evaluator(predictor).measure_accuracy(validation_data)

        print(accuracy)

        self.assertGreaterEqual(accuracy, 0.4)
