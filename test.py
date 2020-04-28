import unittest

from fm_index import FMIndex


class SimpleTest(unittest.TestCase):
    def test_bwt_and_sa(self):
        """
        Test if encode function returns proper bwt and sa arrays
        """
        fm = FMIndex()
        bw, sa = fm.encode('ribaribigrizerep', sa_step=1, tally_step=1)
        self.assertEqual(bw, ['p', 'b', 'i', 'i', 'r', 'z', 'i', 'r', 'r', 'b', 'r', 'e', 'e', '$', 'a', 'g', 'i'])
        self.assertEqual(sa, [16, 3, 2, 6, 14, 12, 8, 1, 5, 7, 10, 15, 13, 0, 4, 9, 11])

    def test_decode(self):
        """
        Test decoding bwt encoded string
        """
        fm = FMIndex()
        bw, sa = fm.encode('ribaribigrizerep', sa_step=1, tally_step=1)
        decoded = fm.decode(bw)
        self.assertEqual(decoded, 'ribaribigrizerep')

    def test_rank_bwt(self):
        """
        Test calculating alphabet ranks of bwt output and character count
        """
        fm = FMIndex()
        bw, sa = fm.encode('ribaribigrizerep', sa_step=1, tally_step=1)
        ranks, ch_count = fm.rank_bwt(bw)
        self.assertEqual(ranks, [0, 0, 0, 1, 0, 0, 2, 1, 2, 1, 3, 0, 1, 0, 0, 0, 3])
        self.assertEqual(ch_count, {'p': 1, 'b': 2, 'i': 4, 'r': 4, 'z': 1, 'e': 2, '$': 1, 'a': 1, 'g': 1})

    def test_calc_sa_checkpoints(self):
        """
        Test calculating SA checkpoints
        """
        fm = FMIndex()
        bw, sa = fm.encode('ribaribigrizerep', sa_step=1, tally_step=1)
        sa_checkpoints = fm.calc_sa_checkpoints(sa, 1)
        self.assertEqual(sa_checkpoints, [16, 3, 2, 6, 14, 12, 8, 1, 5, 7, 10, 15, 13, 0, 4, 9, 11])
        sa_checkpoints = fm.calc_sa_checkpoints(sa, 3)
        self.assertEqual(sa_checkpoints, [None, 3, None, 6, None, 12, None, None, None, None, None, 15, None, 0, None, 9, None])

    def test_calc_tally(self):
        """
        Test calculating Tally matrix checkpoints
        """
        fm = FMIndex()
        bw, sa = fm.encode('ribaribigrizerep', sa_step=1, tally_step=1)

        fm.tally_step = 1
        tally = fm.calc_tally()
        self.assertEqual(tally, [{},
                                 {'p': 1},
                                 {'p': 1, 'b': 1},
                                 {'p': 1, 'b': 1, 'i': 1},
                                 {'p': 1, 'b': 1, 'i': 2},
                                 {'p': 1, 'b': 1, 'i': 2, 'r': 1},
                                 {'p': 1, 'b': 1, 'i': 2, 'r': 1, 'z': 1},
                                 {'p': 1, 'b': 1, 'i': 3, 'r': 1, 'z': 1},
                                 {'p': 1, 'b': 1, 'i': 3, 'r': 2, 'z': 1},
                                 {'p': 1, 'b': 1, 'i': 3, 'r': 3, 'z': 1},
                                 {'p': 1, 'b': 2, 'i': 3, 'r': 3, 'z': 1},
                                 {'p': 1, 'b': 2, 'i': 3, 'r': 4, 'z': 1},
                                 {'p': 1, 'b': 2, 'i': 3, 'r': 4, 'z': 1, 'e': 1},
                                 {'p': 1, 'b': 2, 'i': 3, 'r': 4, 'z': 1, 'e': 2},
                                 {'p': 1, 'b': 2, 'i': 3, 'r': 4, 'z': 1, 'e': 2, '$': 1},
                                 {'p': 1, 'b': 2, 'i': 3, 'r': 4, 'z': 1, 'e': 2, '$': 1, 'a': 1},
                                 {'p': 1, 'b': 2, 'i': 3, 'r': 4, 'z': 1, 'e': 2, '$': 1, 'a': 1, 'g': 1},
                                 {'p': 1, 'b': 2, 'i': 4, 'r': 4, 'z': 1, 'e': 2, '$': 1, 'a': 1, 'g': 1}])

        fm.tally_step = 3
        tally = fm.calc_tally()
        self.assertEqual(tally, [{},
                                 {'p': 1, 'b': 1, 'i': 1},
                                 {'p': 1, 'b': 1, 'i': 2, 'r': 1, 'z': 1},
                                 {'p': 1, 'b': 1, 'i': 3, 'r': 3, 'z': 1},
                                 {'p': 1, 'b': 2, 'i': 3, 'r': 4, 'z': 1, 'e': 1},
                                 {'p': 1, 'b': 2, 'i': 3, 'r': 4, 'z': 1, 'e': 2, '$': 1, 'a': 1}])

    def test_first_col(self):
        """
        Test first column of bwt's transform
        """
        fm = FMIndex()
        bw, sa = fm.encode('ribaribigrizerep', sa_step=1, tally_step=1)
        ranks, ch_count = fm.rank_bwt(bw)
        first = fm.first_col(ch_count)
        self.assertEqual(first, {'$': 1, 'a': (1, 2), 'b': (2, 4), 'e': (4, 6), 'g': (6, 7), 'i': (7, 11),
                                 'p': (11, 12), 'r': (12, 16), 'z': (16, 17)})

    def test_rank_lt(self):
        """
        Test offset of pattern's characters in first column
        """
        fm = FMIndex()
        bw, sa = fm.encode('ribaribigrizerep', sa_step=1, tally_step=1)
        ranks, fm.ch_count = fm.rank_bwt(bw)

        pattern = 'grize'
        rank = [6, 12, 7, 16, 4]
        for i in range(len(pattern)):
            offset = fm.rank_lt(pattern[i])
            self.assertEqual(offset, rank[i])

    def test_get_tally_value(self):
        """
        Test getting value from Tally matrix
        """
        fm = FMIndex()
        bw, sa = fm.encode('ribaribigrizerep', sa_step=1, tally_step=1)

        steps = [1, 3, 5, 7]
        for step in steps:
            fm.tally_step = step
            tally = fm.calc_tally()
            val = fm.get_tally_value(tally, 5, 'i')
            self.assertEqual(val, 2)

    def test_search(self):
        """
        Test searching for the pattern
        """
        fm = FMIndex()
        bw, sa = fm.encode('ribaribigrizerep', sa_step=1, tally_step=1)
        ranks, fm.ch_count = fm.rank_bwt(bw)

        patterns = ['riba', 'grize', 'mamac']
        matches = [[(0, 4)], [(8, 13)], []]
        for i in range(len(patterns)):
            match, start_time, end_time = fm.search(patterns[i])
            self.assertEqual(match, matches[i])


if __name__ == '__main__':
    unittest.main()
