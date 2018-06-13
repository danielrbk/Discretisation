import unittest
import numpy as np

from Implementation.ClassicMethods.Persist import Persist


class TestPersist(unittest.TestCase):

    def test_collapse_matrix_one_cutpoint(self):
        A = [[0, 1, 0, 0], [2, 0, 0, 0], [0, 1, 2, 0], [0, 0, 1, 1]]
        A = np.array(A)
        res = np.array([[6,0],[1,1]])
        cutpoints = [2]

        self.assertEqual(res.tolist(), Persist.collapse_matrix(A, cutpoints).tolist(), "Collapse failed with one cutpoint")

    def test_collapse_matrix_two_cutpoints(self):
        A = [[0, 1, 0, 0], [2, 0, 0, 0], [0, 1, 2, 0], [0, 0, 1, 1]]
        A = np.array(A)
        res = np.array([[3,0,0],[1,2,0],[0,1,1]])
        cutpoints = [1,2]

        self.assertEqual(res.tolist(), Persist.collapse_matrix(A, cutpoints).tolist(), "Collapse failed with two cutpoints")

    def test_collapse_matrix_three_cutpoints(self):
        A = [[0, 1, 0, 0], [2, 0, 0, 0], [0, 1, 2, 0], [0, 0, 1, 1]]
        A = np.array(A)
        res = A
        cutpoints = [0,1,2]

        self.assertEqual(res.tolist(), Persist.collapse_matrix(A, cutpoints).tolist(), "Collapse failed with three cutpoints")



if __name__ == '__main__':
    unittest.main()

