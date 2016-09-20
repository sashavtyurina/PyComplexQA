"""
Set of additional functions. Process dictionaries, split, add, etc.

All methods are static.
NOTE! Please do not add heavy functions here.
"""


class Utils:
    """Static lightweight functions for simple processing."""

    @staticmethod
    def keysFromDictionaryAsList(d):
        """Return a list of keys from the given dictionary."""
        return list(d.keys())


    @ staticmethod
    def extractFromTupleList(tl, n):
        """Given a list of tuples tl, extract n-th member of every tuple. Return a list of the extracted members.

        If not every tuple has n-th member, an IndexError will be raised.

        Ex. tl = [(1,2,3), ('a', 'b', 'c')], then
        extractFromTupleList(tl, 1) will return [2, 'b'].
        """
        result = []
        for t in tl:
            if len(t) > n:
                result.append(t[n])
            else:
                raise IndexError('Tuple ' + str(t) + 'does not have enough elements. ' +
                                 'Trying to extract element #' + n + '.')
        return result
