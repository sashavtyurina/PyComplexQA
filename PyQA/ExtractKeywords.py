import json
import re
from Utils import *

def topWordsFromQuestion(qtitle, qbody):
	processed = preprocessQuestion(qtitle, qbody)
	return processed


def main():
	for line in open('questions.txt'):
		jquestion = json.loads(line.strip())
		print(jquestion['qtitle'] + ' ' + jquestion['qbody'])
		print(topWordsFromQuestion(jquestion['qtitle'], jquestion['qbody']))
		print('\n***\n')

if __name__ == "__main__":
    main()


