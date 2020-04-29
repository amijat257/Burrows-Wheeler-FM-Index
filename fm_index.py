import time
import burrows_wheeler


class FMIndex:
    def __init__(self):
        self.marker = '$'

    def encode(self, text, sa_step=None, tally_step=None):
        """
        Calculate SA, SA with sa_step, Tally matrix and BW transformation
        :param text: input text
        :param sa_step: Suffix Array checkpoint
        :param tally_step: Tally matrix checkpoint
        :return: BWT and Suffix Array
        """
        from main import subtract_times

        # sa_step and tally_step can be added for test purposes
        if not sa_step or not tally_step:
            self.read_steps()
        else:
            self.sa_step = sa_step
            self.tally_step = tally_step

        # Measure time for BW transformation
        bwt_start_time = time.clock()
        self.sa = burrows_wheeler.bwt(text)
        self.sa_checkpoints = self.calc_sa_checkpoints(self.sa, self.sa_step)
        self.bwt = burrows_wheeler.bw_transform(text, self.sa)
        bwt_end_time = time.clock()
        print("BWT execution took %.3fms" % subtract_times(bwt_end_time, bwt_start_time))
        self.tally = self.calc_tally()

        # Calculate ranks and character count
        ranks, ch_count = self.rank_bwt(self.bwt)
        self.ch_count = ch_count
        return self.bwt, self.sa

    def read_steps(self):
        """
        Read steps for Suffix Array and for Tally Matrix
        step is equal to 1 if empty entry
        """
        self.tally_step = input("Insert tally step: ")
        self.tally_step = int(self.tally_step) if self.tally_step != '' else 1
        self.sa_step = int(input("Insert sa step: "))
        self.sa_step = int(self.sa_step) if self.sa_step != '' else 1

    @staticmethod
    def rank_bwt(bw):
        """
        Calculate character ranks of BWT output
        :param bw: BWT column
        :return:  ranks and character count
        """
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
        """
        Reduce taken memory by calculating SA with checkpoints
        :param sa: Suffix Array
        :param steps: Suffix Array step
        :return: reduced Suffix Array
        """
        res = []
        for i in range(len(sa)):
            if (sa[i] % steps) == 0:
                res.append(sa[i])
            else:
                res.append(None)
        return res

    def first_col(self, ch_count):
        """
        Get BWT first column
        :param ch_count: character count
        :return: First column
        """
        fc = {self.marker: 1}
        offset = 1
        for c, count in sorted(ch_count.items()):
            if c != self.marker:
                fc[c] = (offset, offset + count)
                offset += count
        return fc

    def calc_tally(self):
        """
        Calculate Tally matrix for the given
        tally step
        :return: Tally matrix
        """
        A = {}
        C = []
        # Calculate number of character occurrences of BWT output
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
        """
        :param c: index of character in first column
        :return: rank of the given index
        """
        assert self.ch_count is not None
        F = self.first_col(self.ch_count)
        if c in F:
            return F[c][0]
        else:
            return None

    def get_tally_value(self, tally, index, c):
        """
        Get value from the Tally matrix for the given character
        :param tally: Tally matrix
        :param index: Entry in the tally matrix
        :param c: Character
        :return: Tally character rank
        """
        # If the entry is already calculated return the value
        if index % self.tally_step == 0:
            # Return value if character exists, else return 0
            return tally[index//self.tally_step][c] if c in tally[index//self.tally_step] else 0
        else:
            # Tally entry was not calculated so we need to calculate it from the closest checkpoint
            # Get the value for the closest checkpoint
            closest_index = round(index/self.tally_step) * self.tally_step
            if closest_index > len(self.bwt):
                closest_index -= self.tally_step

            # Get row from the closest checkpoint
            closest_row = tally[closest_index//self.tally_step].copy()

            # We need to know if we have to iterate from the closest checkpoint to our index
            # or to iterate to it from our index
            if closest_index > index:
                while closest_index > index:
                    # If the character exists in our checkpoint row decrease it's value
                    if self.bwt[closest_index - 1] in closest_row:
                        closest_row[self.bwt[closest_index - 1]] -= 1
                    # If the value is 0 after decreasing it, remove that character from our row
                    if closest_row[self.bwt[closest_index - 1]] == 0:
                        del closest_row[self.bwt[closest_index - 1]]
                    # Decrease index for next iteration
                    closest_index -= 1
                return closest_row[c] if c in closest_row else 0
            else:
                while closest_index < index:
                    # If the character exists in our checkpoint row increase it's value
                    # else add it to the row
                    if self.bwt[index - 1] in closest_row:
                        closest_row[self.bwt[index - 1]] += 1
                    else:
                        closest_row[self.bwt[index - 1]] = 1

                    # Decrease index for next iteration
                    index -= 1
                return closest_row[c] if c in closest_row else 0

    def search(self, pat):
        """
        Search for the given pattern
        :param pat: Pattern
        :return: matches, time taken for the search
        """
        start_time = time.clock()
        assert self.bwt is not None
        assert self.sa is not None

        # Set boundaries
        begin = 0
        end = len(self.bwt)
        for c in pat[::-1]:
            offset = self.rank_lt(c)
            if offset is None:
                begin, end = None, None
                break

            # Calculate new boundaries where pattern could be found
            begin = offset + self.get_tally_value(self.tally, begin, c)
            end = offset + self.get_tally_value(self.tally, end, c)
            if begin >= end:
                begin, end = None, None
                break

        # Return indexes in original input if pattern is found
        match = []
        if begin is not None and end is not None:
            for i in range(begin, end):
                match.append((self.sa[i], self.sa[i] + len(pat)))

        end_time = time.clock()
        return match, start_time, end_time
