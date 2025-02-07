import csv
import string

def main():

    output = open("tuples.txt", 'w')
    wtr = csv.writer(output, lineterminator = '\n')
    
    fileName = "processed.csv"
    
    rdr = csv.reader(open(fileName, 'r'), delimiter =",", skipinitialspace= True)

    # parse in file
    for row in rdr:

        # evaluate each sentence
        sentence = row[0].translate(str.maketrans('', '', string.punctuation))
        verbs = eval(row[1])
        terms = eval(row[2])
        tuples = search(sentence, verbs, terms)

        # write to output
        for tpl in tuples:
            wtr.writerow(tpl)
    
def search(sentence, verbs, terms):

    lv1terms = list()
    lv2terms = list()
    lv3terms = list()
    
    # classify terms by level
    for term in terms:

        level = getLevel(term[0])

        if level == 1:
            lv1terms.append(term)
        if level == 2:
            lv2terms.append(term)
        if level == 3:
            lv3terms.append(term)

    # build tuples for each term
    tuples_1 = buildTuples(sentence, lv1terms, verbs, 1)
    tuples_2 = buildTuples(sentence, lv2terms, verbs, 2)
    tuples_3 = buildTuples(sentence, lv3terms, verbs, 3)

    return tuples_1 + tuples_2 + tuples_3
        
# returns the break level of a term
def getLevel(term):

    maxlevel = -1
    for element in term.split(":"):
        try:
            i = int(element)
            maxlevel = max(maxlevel, i)
        except ValueError:
            pass

    return maxlevel+1


# returns the left and right indices of a term
def getIndices(termText, sentence):

    lower = -1
    upper = -1
    
    try:
        lower = sentence.index(termText)
        upper = lower + len(termText)
    except ValueError:
        pass
    
    return (lower, upper)


# construct subject-predicate-object tuples
def buildTuples(sentence, terms, verbs, level):

    tuples = list()
    
    beg = -1
    end = -1
    term = ""
    helpers = ['will have','have','had','has','be','is','are','were','will be']

    # iterate through the terms
    for term in terms:

        # get indices
        start, stop = getIndices(term[1], sentence)
        end = start
        
        # search for verbs between terms
        if end > beg:
            for verb in verbs:
                if not sentence.find(verb, beg, end) == -1:
                    words = sentence.split()
                    wordBefore = words[words.index(verb)-1]
                    if wordBefore in helpers:
                        tuples = tuples[:-1]
                        tuples.append([lastTerm[1], wordBefore + " " + verb, term[1], level])
                    else:
                        tuples.append([lastTerm[1], verb, term[1], level])
        beg = stop
        lastTerm = term
        
    return tuples

if __name__ == "__main__":
    main()
