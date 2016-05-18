# these functions will be responsible for extracting keywords from text
from KLDWizard import KLDWizard
from Utils import *

kldWiz = KLDWizard()

def keywordsNFromText(text, N):
	tokens = preprocessText(text).split(' ')
	return kldWiz.topNWordsFromTokens(tokens, N)

# given a list of answers extract N top words from them
# for the foreground model we use frequency of a term between answers as opposed to within answer
def keywordsFromAnswers(answers, N):
    def foregroundDistributionAnswers():
        # compose a string that would respresent between answer frequency
        numAnswers = len(answers)*1.0

        foregroundDistribution = {}
        cleanAnswers = [preprocessText(a) for a in answers]
        cleanAnswers = [a for a in cleanAnswers if not a == '']
        answersTokens = [a.split(' ') for a in cleanAnswers]
        for aTokens in answersTokens:
            uniqueTokens = set(aTokens)

            for ut in uniqueTokens:
                if ut not in foregroundDistribution:
                    foregroundDistribution[ut] = 1.0
                else:
                    foregroundDistribution[ut] += 1.0

        foregroundDistribution.update((k, v/numAnswers) for k,v in foregroundDistribution.items())

    # if there're 3 answers or less we use regular KL divergence
    if len(answers) < 4:
        return keywordsNFromText(' '.join(answers), N)

    foregroundDistribution = foregroundDistributionAnswers(answers)
    return kldWiz.topNWordsFromTokensForeground(foregroundDistribution, N)




