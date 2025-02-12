#
# The spellchecker makes use of the SymSpellPy library.
#
# Install the symspellpy module with:
# pip install -U symspellpy
#

import csv
from symspellpy.symspellpy import SymSpell, Verbosity
import re
import string

def main():

    filePath = "raw.csv"
    outPath = "checked.csv"
    fixesPath = "fixes.csv"
    omitPath = "omit.csv"
    freqPath = "tools\\frequencies.txt"
    dictPath = "tools\\dict_combined.txt"
    
    spellCheck(filePath, freqPath, fixesPath, outPath, omitPath, dictPath)

    
def spellCheck(filePath, freqPath, fixesPath, outPath, omitPath, dictPath):

    file = open(filePath, 'r')
    fileReader = csv.reader(file, delimiter = ",")

    print("Loading dictionaries...")

    # build spell fixer
    sym_spell = SymSpell(3, 7)
    sym_spell.load_dictionary(freqPath, 0, 1)

    # build omissions
    omitFile = open(omitPath, 'r')
    omitReader = csv.reader(omitFile)

    omissions = set()
    next(omitReader)
    for row in omitReader:
        omissions.add(row[0].strip())

    # build dictionary
    dictionary = set()
    dictFile = open(dictPath, 'r')
    for word in dictFile:
        dictionary.add(word.strip())

    # create cleaned output
    outfile = open(outPath, 'w')
    outWriter = csv.writer(outfile, lineterminator = '\n')
    outWriter.writerow(["term", "original", "sentence", "docID"])

    # create change log
    fixFile = open(fixesPath, 'w')
    fixWriter = csv.writer(fixFile, lineterminator = '\n')
    fixWriter.writerow(["orig", "new", "fix", "sentence"])

    # counters
    numUp = 0
    numCor = 0
    numAbb = 0

    print("Searching file...")
    
    next(fileReader)
    for row in fileReader:
        
        term = row[0]
        orig = row[1]
        sentence = row[2]
        sentence = sentence.translate(str.maketrans('', '', string.punctuation))
        words = term.split(":")
        title = False
        
        
        for i in range(len(words)):

            word = words[i]

            # try to get index
            try:
                index = sentence.lower().split().index(word)
                orig = sentence.split()[index]
            except:
                index = -1
                orig = ""
                

            # check if first word of sentence
            firstWord = index == 0

            # word characters only and sufficiently long
            if word.isalpha() and len(word) > 4 and not word.lower() in omissions:

                if (not firstWord and orig.istitle()) or orig == word.upper():

                        numUp += 1
                            
                        words[i] = word.upper()
                        errType = "abbrev"
                        title = True

                
                # if incorrect
                elif not word.lower() in dictionary and orig.islower():
                    
                    # if it's a title, make uppercase and collate
                    if title:

                        #print("MAKE UPPER " + word + "\n")
                            
                        words[i] = word.upper()

                        errType = "abbrev"
                        title = True

                    else:

                        # try to find a replacement
                        fixes = sym_spell.lookup(word, Verbosity.TOP, 1)
                        if(len(fixes) > 0):

                            #print(word + " -> " + fixes[0].term + "\n")
                            numCor += 1
                            words[i] = fixes[0].term

                            if not orig == fixes[0].term:
                                errType = "spelling"
                                   

                elif title:

                    # end title sequence
                    title = False
                        

        
        newTerm = ":".join(words)        
        if not term == newTerm:
            fixWriter.writerow([orig, fixes[0].term, "spelling", sentence])

        outWriter.writerow(row)

    print("Done")
    
    print("Identified " + str(numUp) + " titles and " + str(numCor) + " misspellings.")


if __name__ == "__main__":
    main()
