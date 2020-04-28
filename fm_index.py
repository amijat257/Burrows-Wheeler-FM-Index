import time
import burrows_wheeler


class FMIndex:
    def __init__(self):
        self.marker = '$'

    def encode(self, text, sa_step=None, tally_step=None):
        from main import subtract_times
        self.text_len = len(text)

        if not sa_step or not tally_step:
            self.read_steps()
        else:
            self.sa_step = sa_step
            self.tally_step = tally_step

        bwt_start_time = time.clock()
        self.sa = burrows_wheeler.bwt(text)
        self.sa_checkpoints = self.calc_sa_checkpoints(self.sa, self.sa_step)
        self.bwt = burrows_wheeler.bw_transform(text, self.sa)
        bwt_end_time = time.clock()
        print("BWT execution took %.3fms" % subtract_times(bwt_end_time, bwt_start_time))

        self.tally = self.calc_tally()
        ranks, ch_count = self.rank_bwt(self.bwt)
        self.ch_count = ch_count
        return self.bwt, self.sa

    def decode(self, bwt):
        ranks, ch_count = self.rank_bwt(bwt)
        self.ch_count = ch_count
        first = self.first_col(ch_count)
        t = self.marker
        row_i = 0
        while bwt[row_i] != self.marker:
            c = bwt[row_i]
            t = c + t
            row_i = first[c][0] + ranks[row_i]
        assert (len(t) - 1) == self.text_len

        if t[-1] == self.marker:
            t = t[:-1]
        return t

    def read_steps(self):
        self.tally_step = input("Insert tally step: ")
        self.tally_step = int(self.tally_step) if self.tally_step != '' else 1
        self.sa_step = int(input("Insert sa step: "))
        self.sa_step = int(self.sa_step) if self.sa_step != '' else 1

    def get_steps(self):
        return self.tally_step, self.sa_step

    @staticmethod
    def rank_bwt(bw):
        ch_count = {}
        ranks = []
        for c in bw:
            if c not in ch_count:
                ch_count[c] = 0
            ranks.append(ch_count[c])
            ch_count[c] += 1
        return ranks, ch_count

    @staticmethod
    def calc_sa_checkpoints(sa, steps):
        res = []
        for i in range(len(sa)):
            if (sa[i] % steps) == 0:
                res.append(sa[i])
            else:
                res.append(None)
        return res

    def first_col(self, ch_count):
        fc = {self.marker: 1}
        offset = 1
        for c, count in sorted(ch_count.items()):
            if c != self.marker:
                fc[c] = (offset, offset + count)
                offset += count
        return fc

    def calc_tally(self):
        A = {}
        C = []
        for i, c in enumerate(self.bwt):
            if i % self.tally_step == 0:
                C.append(A.copy())
            if A.get(c):
                A[c] += 1
            else:
                A[c] = 1
        if i % self.tally_step == 0:
            C.append(A.copy())
        return C

    def rank_lt(self, c):
        assert self.ch_count is not None
        F = self.first_col(self.ch_count)
        if c in F:
            return F[c][0]
        else:
            return None

    def get_tally_value(self, tally, index, c):
        if index % self.tally_step == 0:
            return tally[index//self.tally_step][c] if c in tally[index//self.tally_step] else 0
        else:
            closest_index = round(index/self.tally_step) * self.tally_step
            if closest_index > len(self.bwt):
                closest_index -= self.tally_step
            closest_row = tally[closest_index//self.tally_step].copy()
            if closest_index > index:
                while closest_index > index:
                    if self.bwt[closest_index - 1] in closest_row:
                        closest_row[self.bwt[closest_index - 1]] -= 1
                    if closest_row[self.bwt[closest_index - 1]] == 0:
                        del closest_row[self.bwt[closest_index - 1]]
                    closest_index -= 1
                return closest_row[c] if c in closest_row else 0
            else:
                while closest_index < index:
                    if self.bwt[index - 1] in closest_row:
                        closest_row[self.bwt[index - 1]] += 1
                    else:
                        closest_row[self.bwt[index - 1]] = 1
                    if closest_row[self.bwt[index - 1]] == 0:
                        del closest_row[self.bwt[index - 1]]
                    index -= 1
                return closest_row[c] if c in closest_row else 0

    def search(self, pat):
        start_time = time.clock()
        assert self.bwt is not None
        assert self.sa is not None

        begin = 0
        end = len(self.bwt)
        for c in pat[::-1]:
            offset = self.rank_lt(c)
            if offset is None:
                begin, end = None, None
                break

            begin = offset + self.get_tally_value(self.tally, begin, c)
            end = offset + self.get_tally_value(self.tally, end, c)
            if begin >= end:
                begin, end = None, None
                break

        match = []
        if begin is not None and end is not None:
            for i in range(begin, end):
                match.append((self.sa[i], self.sa[i] + len(pat)))

        end_time = time.clock()
        return match, start_time, end_time
