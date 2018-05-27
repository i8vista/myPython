#! python3
# randomQuizGenerator.py - Creates quizzes with questions and answers in
# random order,along with the answer key.

import random

# The quiz data, Keys are states and values are their capitals.
capitals = {'Alabama': 'Montgomery', 'Alska': 'Juneau', 'Arizona': 'Phoenix',
            'Arkansas': 'Little Rock', 'California': 'Sacramento', 'Clorado': 'Denver',
            'Connecticut': 'Hartford', 'Delaware': 'Dover', 'Florida': 'Tallahassee',
            'Georgia': 'Atlanta', 'Hawaii': 'Honolulu', 'Idaho': 'Boise',
            'Illinois': 'Springfield', 'Indiana': 'Indianaolis', 'Iowa': 'Des Moines',
            'Kansas': 'Topeka', 'Kentucky': 'Frankfort', 'Louisiana': 'Baton Rouge',
            'Maine': 'Augusta', 'Maryland': 'Annapolis', 'Massachusetts': 'Boston',
            'Michigan': 'Lansing', 'Minnesota':'St.Paul','Mississippi':'Jackson',
            'Missouri':'Jefferson City','Montana': 'Helena', 'Nebraska': 'Lincoin',
            'Nevada': 'Carson City', 'New Hampshire': 'Concord', 'New Jersey': 'Trenton',
            'New Mexico': 'Santa Fe', 'New York': 'Albany', 'North carlona': 'Raleigh',
            'North Dakota': 'Bismarck', 'Ohio': 'Columbus', 'Oklahoma': 'Oklahoma City',
            'Oregon': 'Salem', 'Pennsylvania': 'Harrisburg', 'Rhode Island': 'Providence',
            'South Carolina': 'Columbia', 'South Dakota': 'pierre', 'Tennessee': 'Nashville',
            'Texas': 'Austin', 'Utah': 'Salt Lake City', 'Vermont': 'Montpelier',
            'Virginia': 'Richmond', 'Washington': 'Olmpia', 'West Virginia': 'Charlestion',
            'Wisconsin': 'Madison', 'Wyoming': 'Cheyenne'}
# Generate 35 quiz files.
for quizNum in range(35):
    # Create the quiz and answer key files.
    quizFile = open('capitalsquiz%s.txt' % (quizNum + 1),'w')
    answerKeyFile = open('capitalsquiz_answers%s.txt' % (quizNum + 1),'w')

    # Write out the header for the quiz.
    quizFile.write('Name:\nData:\n\nPeriod:\n\n')
    quizFile.write((' '*20)+'State Capitals Quiz (Form %s)' % (quizNum +1))
    quizFile.write('\n\n')
    
    # Shuffle the order of the states.
    states = list(capitals.keys())
    random.shuffle(states)

    # Loop through all 50 states, making a question for each.
    for questionNum in range(50):
        currectAnswer = capitals[states[questionNum]] 
        wrongAnswers = list(capitals.values())
        wrongAnswers.remove(currectAnswer)
        wrongAnswers = random.sample(wrongAnswers,3)
        answerOptions = wrongAnswers + [currectAnswer]
        random.shuffle(answerOptions)

        # Write the quesstion and answer options to the quiz file.
        quizFile.write('%s. What the capital of %s?\n' % (questionNum+1,states[questionNum]))
        for i in range(4):
            quizFile.write(' %s. %s\n' % ('ABCD'[i],answerOptions[i]))
        quizFile.write('\n')

        # Write the answer key to a file.
        answerKeyFile.write('%s. %s\n' % (questionNum +1,'ABCD'[answerOptions.index(currectAnswer)]))
    quizFile.close()
    answerKeyFile.close()

