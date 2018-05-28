madLibsFile = open('Mad Libs.txt')
madLibsList = madLibsFile.read().split()
for i in range(len(madLibsList)):
    if madLibsList[i] == 'ADJECTIVE' or madLibsList[i] == 'NOUN' or madLibsList[i] == 'ADVERB' or madLibsList[i] == 'VERB':
        print('Enter an %s:' % madLibsList[i].lower())
        madLibsList[i] = input()
    elif madLibsList[i] == 'ADJECTIVE.' or madLibsList[i] == 'NOUN.' or madLibsList[i] == 'ADVERB.' or madLibsList[i] == 'VERB.':
        print('Enter an %s:' % madLibsList[i].lower())
        madLibsList[i] = input() + '.'
newMadLibsFile = open('New Mad Libs.txt','w')
newMadLibsFile.write(' '.join(madLibsList))
print(' '.join(madLibsList))
madLibsFile.close()
newMadLibsFile.close()
