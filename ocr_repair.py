# -*- coding: utf-8 -*-
import json
from fix_tools import *
import re
import operator

with open("resources/testword_list.txt", "r", encoding="utf-8") as f:
    testword_list = [ re.sub("\n", "", x) for x in f]

with open("resources/fix_data.tsv", "r", encoding="utf-8") as f:
    corrections = [parse_data_row(re.sub("\n", "", x)) for x in f]

with open("resources/test_list.txt", "r", encoding="utf-8") as f:
    test_list = [re.sub("\n", "", x) for x in f]

with open("resources/trigram_list.json", "r", encoding="utf-8") as f:
    trigram_table = json.load(f)

ensure_dbs()

# necessary resources are built here.

correction_list = parse_corrections_to_list(corrections)
split_list = get_split_list(correction_list)
character_frequency_table = get_character_frequency_table(testword_list)
replacement_probabilities = build_replacement_probability_table(correction_list, character_frequency_table)

def analyse_word(word):
# the word in iterated character by character and a matrix is built based on each possible replacement character for each character in the word. Also splitting characters are taken in to account.
# the matrix is passed through to run_through_matrix(), which calculates individual probabilities of each possible route through the matrix. Only 100 most probable possibilities are chosen to be analysed for the next step through the matrix.

    correction_matrix = []
    
    for i in range(0, len(word)):

        c = word[i]
        if c not in replacement_probabilities: c = "unknown" 
       
        if len(replacement_probabilities[c]) > 1:
            possibilities = [c]
            split_pos = check_split_list(split_list, word[i:])        
            possibilities.extend(split_pos)
            row = dict()
            factor = 1
            for pos in possibilities:

                if len(pos) > 1: 
                    factor = replacement_probabilities[pos][pos]

            for pos in possibilities:
                   	
                        
                for rep in replacement_probabilities[pos]: 
                    rep_s = add_split_marks(rep, len(pos))
                    if len(pos) == 1: f = factor
                    else: f = 1
                    if len(pos) > 1 and rep == pos:
                        that = True
                    else:row.update({ rep_s : replacement_probabilities[pos][rep]*f })
           
            correction_matrix.append(row)
            
        else:
            correction_matrix.append( { c : 1 } )
      
    guesses = run_through_matrix(word, correction_matrix, trigram_table)

    return guesses        
 

def calculate_final_probabilities(guesses):

    probabilities = dict()
    for guess in guesses:
        factor = get_word_probability(guess["fragment"])
        probabilities.update( { guess["fragment"] : guess["prob"]*factor } )

    return probabilities

def analyse(word, n=3):
# word is the word to be analysed
# n is the length of the list of most probable outcomes returned
# analyse_word() returns 100 most probable guesses, calculate_final_probabilities() assigns them new probabilities taking account the outputs probability in a wordlist.

    guesses = analyse_word(word)
    guesses = calculate_final_probabilities(guesses)
    guesses = sorted(guesses.items(), key=operator.itemgetter(1), reverse=True)
    
    return guesses[0:int(n)]


#        if i < 11 :print(word, guesses[i])
#        if guesses[i][0] == "maksakoon": 
#            print(i, word, guesses[i])
#            maksakoon = guesses[i]
        
        
#print(word_probability_table["kostaaksensa"]*maksakoon[1]/word_probability_table["nonce"])          
#print(correction_probabilities["f"])
#print(scramble_probabilities["f"])
