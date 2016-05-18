# these functions will be responsible for extracting keywords from text
from KLDWizard import KLDWizard as kldWiz
from Utils import *

def keywordsNFromText(text):
	tokens = preprocessText(text).split(' ')
	return topNWordsFromTokens(tokens, N)
