"""Descibe a class that deals with KL divergence."""

import math
from operator import itemgetter


class KLDWizard:
    """Class that will help figure out word frequencies and KL divergence."""

    # dictionary contains probabilities of words in ClueWeb09b. Background probabilities.
    wordProbabilities = {}

    def __init__(self, wordFrequenciesFilename):
        """Pull global word frequencies from a WordFrequencies.txt file."""
        for line in open(wordFrequenciesFilename):
            word, frequency, totalWords = line.strip().split('|')
            frequency = int(frequency)
            totalWords = int(totalWords)
            self.wordProbabilities[word] = (frequency * 1.0) / (totalWords * 1.0)
            self.totalWordsClueweb = totalWords

    @staticmethod
    def buildForegroundModel(tokens):
        """Build a foreground probability given a list of tokens."""
        result = {}

        for t in tokens:
            if t not in result:
                result[t] = 1.0
            else:
                result[t] += 1.0

        for t in result.keys():
            result[t] /= (len(tokens) * 1.0)

        return result


    def wordKLD(self, word, foregroundProbability):
        """Calculate pointwise KL divergence value for a given word and foreground model."""
        if word not in self.wordProbabilities:
            raise KeyError('KLD score for ' + word + ' could not be calculated, because ' +
                           word + ' is not in WordFrequencies.txt')

        backgroundProbability = self.wordProbabilities[word]
        P = foregroundProbability
        Q = backgroundProbability

        # kl divergence is not defined
        if Q == 0:
            print(word + ' has a count of zero in WordFrequencies.txt. Setting background probability to min possible.')
            Q = 1 / self.totalWordsClueweb

        return P * math.log(P / Q)


    def topNWordsFromTokens(self, tokens, N):
        """Return N scored tokens with the highest KLD scores."""
        foreground = KLDWizard.buildForegroundModel(tokens)

        return self.topNWordsFromTokensForeground(foreground, N)

        # scoredWords = {}
        # for t in foreground.keys():
        #     kldScore = self.wordKLD(t, foreground[t])
        #     # if not kldScore == -1:
        #     scoredWords[t] = kldScore

        # sortedScoredWords = sorted(scoredWords.items(), key=itemgetter(1), reverse=True)

        # # if N == -1 return all tokens
        # if N == -1:
        #     N = len(sortedScoredWords)
        # return sortedScoredWords[:N]


    def topNWordsFromTokensForeground(self, foregroundModel, N):
        """Return a list N scored tokens with the higest KL divergence scores, given a foreground model."""
        scoredWords = {}
        for t in foregroundModel.keys():
            kldScore = self.wordKLD(t, foregroundModel[t])
            scoredWords[t] = kldScore  # self.wordKLD(t, foregroundModel[t])

        sortedScoredWords = sorted(scoredWords.items(), key=itemgetter(1), reverse=True)

        # if N == -1 return all tokens
        if N == -1:
            N = len(sortedScoredWords)
        return sortedScoredWords[:N]



