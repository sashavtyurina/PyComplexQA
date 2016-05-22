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
            print(word + ' not in the file')
            return -1
        backgroundProbability = self.wordProbabilities[word]
        P = foregroundProbability
        Q = backgroundProbability


        # kl divergence is not defined
        if Q == 0:
            Q = 1/self.totalWordsClueweb
        return P * math.log(P/Q)


    # returns a list of N words with the highest KLD score
    def topNWordsFromTokens(self, tokens, N):
        foreground = KLDWizard.foregroundModel(tokens)

        scoredWords = {}
        for t in foreground.keys():
            kldScore = self.wordKLD(t, foreground[t])
            if not kldScore == -1:
                scoredWords[t] = kldScore
        # print(scoredWords.items())
        sortedScoredWords = sorted(scoredWords.items(), key=itemgetter(1), reverse=True)
        # print(sortedScoredWords)
        if N == -1:
            return sortedScoredWords
        return sortedScoredWords[:N]

    # same as topNWordsFromTokens, only with a foreground model given
    def topNWordsFromTokensForeground(self, foregroundModel, N):
        scoredWords = {}
        for t in foregroundModel.keys():
            scoredWords[t] = self.wordKLD(t, foregroundModel[t])

        sortedScoredWords = sorted(scoredWords.items(), key=itemgetter(1), reverse=True)
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
