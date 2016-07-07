"""Class that deals with KL divergence scores."""
import math
from operator import itemgetter


class KLDWizard:
    """Class that will help figure out word frequencies and KL divergence."""

    wordProbabilities = {}

    def __init__(self):
        """Pull global word frequencies from a file."""
        for line in open('WordFrequencies.txt'):
            # print(line)
            word, frequency, totalWords = line.strip().split('|')
            frequency = int(frequency)
            totalWords = int(totalWords)
            self.wordProbabilities[word] = (frequency * 1.0) / (totalWords * 1.0)
            self.totalWordsClueweb = totalWords


    def wordKLD(self, word, foregroundProbability):
        """Calculate pointwise KL divergence value for a given word and foreground model."""
        missingWords = open('missing words.txt', 'a')
        if word not in self.wordProbabilities:
            missingWords.write('%s\n' % word)
            print(word + ' not in the file')
            return -1
        backgroundProbability = self.wordProbabilities[word]
        P = foregroundProbability
        Q = backgroundProbability

        # kl divergence is not defined
        if Q == 0:
            Q = 1 / self.totalWordsClueweb

        missingWords.close()
        return P * math.log(P / Q)


    def topNWordsFromTokens(self, tokens, N):
        """Return N scored tokens with the highest KLD scores."""
        foreground = KLDWizard.foregroundModel(tokens)

        scoredWords = {}
        for t in foreground.keys():
            kldScore = self.wordKLD(t, foreground[t])
            if not kldScore == -1:
                scoredWords[t] = kldScore

        sortedScoredWords = sorted(scoredWords.items(), key=itemgetter(1), reverse=True)

        # if N == -1 return all tokens
        if N == -1:
            N = len(sortedScoredWords)
        return sortedScoredWords[:N]


    def topNWordsFromTokensForeground(self, foregroundModel, N):
        """Return a list N scored tokens with the higest KL divergence scores, given a foreground model."""
        scoredWords = {}
        for t in foregroundModel.keys():
            scoredWords[t] = self.wordKLD(t, foregroundModel[t])

        sortedScoredWords = sorted(scoredWords.items(), key=itemgetter(1), reverse=True)

        # if N == -1 return all tokens
        if N == -1:
            N = len(sortedScoredWords)
        return sortedScoredWords[:N]


    def foregroundModel(tokens):
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
