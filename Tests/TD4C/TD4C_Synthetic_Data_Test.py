import csv
import unittest
from typing import Dict, List

from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.ClassicMethods.EQW import EqualWidth
from Implementation.ClassicMethods.Persist import Persist
from Implementation.DataObject import DataObject
from Implementation.InputHandler import get_maps_from_file
from Implementation.TimeInterval import TimeInterval
from Implementation.TD4C.TD4C import TD4C
from Tests.Discretization_Result_Generator import get_test_result, assert_almost_equality
from Tests.Constants import DATASETS_PATH

DATASET_NAME = "Synthetic_TD4C"
CLASS_SEPERATOR = 55

DATASET_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + ".csv"
EXPECTED_OUTPUT_PATH = DATASETS_PATH + "\\" + DATASET_NAME + "\\" + DATASET_NAME + "_"
m1, m2, m3 = get_maps_from_file(DATASET_PATH, CLASS_SEPERATOR)


class TestMethods(unittest.TestCase):

    def setUp(self):
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3

    def test_EQF_5(self):
        d = EqualFrequency(5)
        name = "EQF5"

        path = EXPECTED_OUTPUT_PATH + name + ".csv"
        real, expected = get_test_result(path, self.m1, self.m2, self.m3, d)
        result, message = assert_almost_equality(real, expected)
        self.assertTrue(result, message)

    def test_populate_state_vector(self):
        d = EqualFrequency(5)
        d1, d2, d3 = d.discretize(self.m1, self.m2, self.m3)
        real_class_to_state_vector = TD4C.populate_state_vector(d1, d2, d3, 4, 1)
        expected_class_state_vector = {1: [1, 1, 0, 1, 2], 0: [1, 1, 2, 1, 0]}
        self.assertEqual(real_class_to_state_vector, expected_class_state_vector)

    def test_calculate_probability_vector_1_point_edge(self):
        d = EqualFrequency(5)
        d1, d2, d3 = d.discretize(self.m1, self.m2, self.m3)
        class_to_state_vector = {1: [1, 1, 0, 1, 2], 0: [1, 1, 2, 1, 0]}
        real_probability_vector = TD4C.calculate_probability_vector(class_to_state_vector, [0])
        expected_probability_vector = {1: [0.2, 0.8], 0: [0.2, 0.8]}
        self.assertEqual(real_probability_vector, expected_probability_vector)

    def test_calculate_probability_vector_1_point_other_edge(self):
        d = EqualFrequency(5)
        d1, d2, d3 = d.discretize(self.m1, self.m2, self.m3)
        class_to_state_vector = {1: [1, 1, 0, 1, 2], 0: [1, 1, 2, 1, 0]}
        real_probability_vector = TD4C.calculate_probability_vector(class_to_state_vector, [3])
        expected_probability_vector = {1: [0.6, 0.4], 0: [1, 0]}
        self.assertEqual(real_probability_vector, expected_probability_vector)

    def test_calculate_probability_vector_2_points(self):
        d = EqualFrequency(5)
        d1, d2, d3 = d.discretize(self.m1, self.m2, self.m3)
        class_to_state_vector = {1: [1, 1, 0, 1, 2], 0: [1, 1, 2, 1, 0]}
        real_probability_vector = TD4C.calculate_probability_vector(class_to_state_vector, [1,3])
        expected_probability_vector = {1: [0.4, 0.2, 0.4], 0: [0.4, 0.6, 0]}
        self.assertEqual(real_probability_vector, expected_probability_vector)

    def test_cosine_chosen_indices_first_cutoff(self):
        d = TD4C(4, TD4C.Cosine, ACCURACY_MEASURE=5)
        d1, d2, d3 = d.discretize(self.m1, self.m2, self.m3)
        real_first_cutoff = d.cutoffs_according_to_order[1][0]
        real_first_score = d.chosen_scores[1][0]
        expected_first_cutoff = 6.5
        expected_first_score = 0.7378150601
        self.assertEqual(real_first_cutoff,expected_first_cutoff)

    def test_cosine_chosen_indices_first_score(self):
        d = TD4C(4, TD4C.Cosine, ACCURACY_MEASURE=5)
        d1, d2, d3 = d.discretize(self.m1, self.m2, self.m3)
        real_first_index = d.cutoffs_according_to_order[1][0]
        real_first_score = d.chosen_scores[1][0]
        expected_first_index = 2
        expected_first_score = 0.7378150601
        epsilon = 10**-8
        difference = abs(real_first_score-expected_first_score)
        self.assertTrue(difference < epsilon, "Difference is %s, larger than %s" % (difference, epsilon))

    def test_cosine_chosen_indices_second_cutoff(self):
        d = TD4C(4, TD4C.Cosine, ACCURACY_MEASURE=5)
        d1, d2, d3 = d.discretize(self.m1, self.m2, self.m3)
        real_cutoff = d.cutoffs_according_to_order[1][1]
        real_score = d.chosen_scores[1][1]
        expected_cutoff = 2.5
        expected_score = 0.881021326
        self.assertEqual(real_cutoff,expected_cutoff)

    def test_cosine_chosen_indices_second_score(self):
        d = TD4C(4, TD4C.Cosine, ACCURACY_MEASURE=5)
        d1, d2, d3 = d.discretize(self.m1, self.m2, self.m3)
        real_cutoff = d.cutoffs_according_to_order[1][1]
        real_score = d.chosen_scores[1][1]
        expected_cutoff = 2.5
        expected_score = 0.881021326
        epsilon = 10**-8
        difference = abs(real_score-expected_score)
        self.assertTrue(difference < epsilon, "Difference is %s, larger than %s" % (difference, epsilon))

    def test_cosine_chosen_indices_third_cutoff(self):
        d = TD4C(4, TD4C.Cosine, ACCURACY_MEASURE=5)
        d1, d2, d3 = d.discretize(self.m1, self.m2, self.m3)
        real_cutoff = d.cutoffs_according_to_order[1][2]
        real_score = d.chosen_scores[1][2]
        expected_cutoffs = [4.5,8.5]
        expected_score = 0.881021326
        self.assertIn(real_cutoff, expected_cutoffs)

    def test_cosine_chosen_indices_third_score(self):
        d = TD4C(4, TD4C.Cosine, ACCURACY_MEASURE=5)
        d1, d2, d3 = d.discretize(self.m1, self.m2, self.m3)
        real_cutoff = d.cutoffs_according_to_order[1][2]
        real_score = d.chosen_scores[1][2]
        expected_cutoff = 2.5
        expected_score = 0.9645303579
        epsilon = 10**-8
        difference = abs(real_score-expected_score)
        self.assertTrue(difference < epsilon, "Difference is %s, larger than %s" % (difference, epsilon))




if __name__ == '__main__':
    unittest.main()

