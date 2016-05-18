import math
from operator import itemgetter

class KLDWizard:
    # class that will help figure out word frequencies and KL divergence

    wordProbabilities = {}
    def __init__(self):

        # load the word frequencies
        for line in open('WordFrequencies.txt'):
            word, frequency, totalWords = line.strip().split('|')
            # print(frequency)
            # print(int(frequency))
            frequency = int(frequency)
            totalWords = int(totalWords)


            self.wordProbabilities[word] = (frequency*1.0)/(totalWords*1.0)
            self.totalWordsClueweb = totalWords

    # calculates KL divergence of a single word
    def wordKLD(self, word, foregroundProbability):
        if word not in self.wordProbabilities:
            return -1
        backgroundProbability = self.wordProbabilities[word]
        P = foregroundProbability
        Q = backgroundProbability
        return P * math.log(P/Q)


    # returns a list of N words with the highest KLD score
    def topNWordsFromTokens(self, tokens, N):
        foreground = KLDWizard.foregroundModel(tokens)

        scoredWords = {}
        for t in foreground.keys():
            scoredWords[t] = self.wordKLD(t, foreground[t])

        sortedScoredWords = sorted(scoredWords, key=itemgetter(1), reverse=True)
        print(sortedScoredWords)
        return sortedScoredWords[:N]


    # given a list of tokens builds a foreground distibution model
    def foregroundModel(tokens):
        result = {}

        for t in tokens:
            if t not in result:
                result[t] = 1.0
            else:
                result[t] += 1.0

        for t in result.keys():
            result[t] /= (len(tokens)*1.0)

        return result
