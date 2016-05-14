import json
import re
from Utils import *
import itertools




def main():
	distinctWords = set()
	for line in open('questions.txt'):
		jquestion = json.loads(line.strip())
		question = jquestion['qtitle'].lower() + ' ' + jquestion['qbody'].lower()
		qtokens = preprocessText(question).split(' ')
		atokens = [preprocessText(a['answer']).lower().split(' ') for a in jquestion['answers']]
		atokens = list(itertools.chain(*atokens))
		distinctWords.update(qtokens)
		distinctWords.update(atokens)

		print(distinctWords)
		print('\n***\n')

	with open('distinctWordsQA.txt', 'w') as f:
		for w in distinctWords:
			f.write('%s\n' %w)

if __name__ == "__main__":
    main()


