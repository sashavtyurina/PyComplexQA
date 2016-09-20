"""Additional functions that deal with queries in different aspects.

Single class is described in this file, with all its methods being static.
"""

from Utils import Utils
import operator


class QueryWizard:
    """Functions to deal with queries."""

    @staticmethod
    def repeatingNgrams(tokens):
        """Find n-grams that repeat at least 2 times in the given list of tokens.

        Ex. a b c a b c d, should return a b.
        We will use repeated n-grams as separate tokens to create probe queries from.

        Prior to spl
        """
        return 1


    @staticmethod
    def sortTokens(initialTokens, tokensToSort):
        """Put tokensToSort in the same order that they appear in tokens.

        tokensToSort    is a list top scored tokens, selected for probe query construction
        initialTokens   is a list of question tokens, after preprocessing.

        Initially create a dictionary containing each token's index in the initial question.
        Sort tokens based on their indexes. Return sorted list.
        """
        tokensInd = {}
        for t in tokensToSort:
            if t not in initialTokens:
                raise KeyError('Token ' + t + ' was not found in the list of raw question tokens')

            ind = initialTokens.index(t)
            tokensInd[t] = ind
        sortedInd = sorted(tokensInd.items(), key=operator.itemgetter(1))
        return Utils.extractFromTupleList(sortedInd, 0)


    @staticmethod
    def generateQueries(tokens, queryLength):
        """Construct all queries of length queryLength out of given list of tokens."""
        def addOne(queries, tokens):
            newQueries = {}
            for q in queries.items():
                for i in range(q[1] + 1, len(tokens)):
                    # TODO: handle this more gracefully
                    # check if these tokens (or bigrams) overlap
                    if len(set(q[0].split()).intersection(set(tokens[i].split()))) == 0:
                        qq = ' '.join([q[0], tokens[i]])
                        newQueries[qq] = max(q[1], i)
            return newQueries


        queriesOfLengths = {}
        queries = {}

        # start by creating all single word queries
        for i in range(0, len(tokens)):
            queries[tokens[i]] = i
        queriesOfLengths[1] = queries.keys()

        # append one word to existing queries
        for i in range(1, queryLength):
            queries = addOne(queries, tokens)
            queriesOfLengths[i + 1] = queries.keys()

        return queriesOfLengths[queryLength]
