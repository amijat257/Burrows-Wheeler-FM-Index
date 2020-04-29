from operator import itemgetter
from itertools import groupby

marker = '$'


def bw_transform(t, sa):
    transform = []
    for idx in sa:
        if idx == 0:
            transform += marker
        else:
            transform += [t[idx - 1]]
    return transform


def bwt(input_string):
    """
    Calculate Suffix Array
    :param input_string:
    :return: Suffix Array
    """
    data_ref = suffix_array(input_string)

    # We add len(data_ref) at the beginning as it
    # represents terminal value
    return [len(data_ref)] + data_ref


def suffix_array(text, _step=1):
    """
        Analyze all common strings in the text.
        Short substrings of the length _step a are first pre-sorted. The are the
        results repeatedly merged so that the garanteed number of compared
        characters bytes is doubled in every iteration until all substrings are
        sorted exactly.
        Arguments:
            text:  The text to be analyzed.
            _step: Is only for optimization and testing. It is the optimal length
                   of substrings used for initial pre-sorting. The bigger value is
                   faster if there is enough memory. Memory requirements are
                   approximately (estimate for 32 bit Python 3.3):
                       len(text) * (29 + (_size + 20 if _size > 2 else 0)) + 1MB
        Return value:
        sa:  Suffix array                  for i in range(1, size):
               assert text[sa[i-1]:] < text[sa[i]:]
       """
    tx = text
    size = len(tx)
    step = min(max(_step, 1), len(tx))
    sa = list(range(len(tx)))
    sa.sort(key=lambda i: tx[i:i + step])
    grpstart = size * [False] + [True]  # a boolean map for iteration speedup.
    # It helps to skip yet resolved values. The last value True is a sentinel.
    rsa = size * [None]
    stgrp, igrp = '', 0
    for i, pos in enumerate(sa):
        st = tx[pos:pos + step]
        if st != stgrp:
            grpstart[igrp] = (igrp < i - 1)
            stgrp = st
            igrp = i
        rsa[pos] = igrp
        sa[i] = pos
    grpstart[igrp] = (igrp < size - 1 or size == 0)
    while grpstart.index(True) < size:
        nextgr = grpstart.index(True)
        while nextgr < size:
            igrp = nextgr
            nextgr = grpstart.index(True, igrp + 1)
            glist = []
            for ig in range(igrp, nextgr):
                pos = sa[ig]
                if rsa[pos] != igrp:
                    break
                newgr = rsa[pos + step] if pos + step < size else -1
                glist.append((newgr, pos))
            glist.sort()
            for ig, g in groupby(glist, key=itemgetter(0)):
                g = [x[1] for x in g]
                sa[igrp:igrp + len(g)] = g
                grpstart[igrp] = (len(g) > 1)
                for pos in g:
                    rsa[pos] = igrp
                igrp += len(g)
        step *= 2
    del grpstart

    return sa
