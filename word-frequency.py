import csv
import re 
import nltk
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords

import pprint
import json

'''
    bigrams/trigrams for context??
    make dictionary of single words and frequency

    find stopwords!!
    print dictionary to a text file
    look at top like 50/100 words
''' 

frequencies = {}

stop_words = stopwords.words('english')
# make another list of stopwords to add to this, like '6pm' and phon numbers and 'lindsey cormack'

def count_words(email):
    for word in email:
        if(word in frequencies):
            frequencies[word] += 1
        else:
            frequencies[word] = 1

if __name__ == '__main__':
    f = open('stopwords_lindsey.txt','r')
    line = f.readline()
    try:
        while line:
            # don't include \n character
            stop_words = stop_words + [line[0:len(line)-1].lower()]
            line = f.readline()
    except StopIteration:
        pass
    print('COVID-19 Congressional Emails Word Count')

    try:
        month = int(input('Month in 2020 (1-6, or say 0 to count each email): '))
        while (month > 6 or month < 0):
            month = int(input('Month in 2020 (1-6, or say 0 to count each email): '))
    except ValueError:
        month = 0


    party = input('Democrat or Republican? (D or R): ')
    #try:
    while not (len(party) == 1 and (party.lower() == 'd' or party.lower() == 'r')):
        party = input('Democrat or Republican? (D or R): ')


    data_file_name = 'covid19-dem-emails-and-data.csv' if party.lower() == 'd' else 'covid19-rep-emails-and-data.csv'

    data = open(data_file_name,newline='')

    data_reader = csv.reader(data)
    data_row = next(data_reader) # skip column labels
    data_row = next(data_reader)
    try:
        while data_row:
            email_date = data_row[0]
            email_month = int(email_date[0:email_date.index('/')])
            if(month == 0 or email_month == month):
                email = [w for w in word_tokenize(data_row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
                count_words(email)
            elif(email_month < month):
                break
            data_row = next(data_reader)
    except StopIteration:
        print('done')
     
    frequencies = {k : v for k, v in sorted(frequencies.items(), key=lambda item: item[1],reverse=True) if v > 1}
    frequencies_file_name = ""
    if(month == 0):
        frequencies_file_name = ('dem-frequencies.txt') if party.lower() == 'd' else ('rep-frequencies.txt')
    else:
        frequencies_file_name = ('dem-frequencies-'+ str(month) +'-2020.txt') if party.lower() == 'd' else ('rep-frequencies-'+ str(month) +'-2020.txt')

    with open(frequencies_file_name,'w') as file:
        party_string = 'Democrat' if party.lower() == 'd' else 'Republican'
        if(month > 0):
            file.write("Word Frequencies in " + party_string + " Emails during "+ str(month) + "/2020\n")
        else:
            file.write("Word Frequencies in " + party_string + " Emails")
        for k,v in frequencies.items():
            file.write(k + ": " + str(v) +"\n")
    