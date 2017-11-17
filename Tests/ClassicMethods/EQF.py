import unittest
from Implementation.ClassicMethods.EQF import EqualFrequency
from Implementation.DataObject import DataObject
from Implementation.TimeInterval import TimeInterval


class TestEqualFrequency(unittest.TestCase):
    def test_easy_data(self):
        easyData = DataObject([('a', TimeInterval(x, x), x) for x in range(11)])
        easyBins = 4
        easyBinRanges = [1.5,4.5,7.5]
        eqw = EqualFrequency(easyData, easyBins)
        self.assertEqual(easyBinRanges, eqw.bin_ranges)

    def test_medium_data(self):
        mediumData = DataObject([('a', TimeInterval(-100, -100), -10000)] +
                                [('a', TimeInterval(x, x), x) for x in range(11)] +
                                [('a', TimeInterval(100, 100), 10000)])
        mediumBins = 4
        mediumWidth = (10000*2) / mediumBins
        mediumBinRanges = [1.5,4.5,7.5]
        eqw = EqualFrequency(mediumData, mediumBins)
        self.assertEqual(mediumBinRanges, eqw.bin_ranges)

    def test_hard_data(self):
        hardData = DataObject([('a', TimeInterval(x, x), 5) for x in range(100)])
        hardBins = 4
        hardWidth = 0
        hardBinRanges = [5,5,5]
        eqw = EqualFrequency(hardData, hardBins)
        self.assertEqual(hardBinRanges, eqw.bin_ranges)

if __name__ == '__main__':
    unittest.main()

