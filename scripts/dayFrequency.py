import csv
import re 
import nltk
import matplotlib.pyplot as plt
import pandas as pd

from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from nltk.util import ngrams

stop_words = "" 

dem_email_counts = {}
rep_email_counts = {}

# update_stopwords
def update_stopwords():
    sw = stopwords.words('english')
    f = open('../frequencies/stopwords_lindsey.txt','r')
    line = f.readline()
    try:
        while line:
            # don't include \n character
            word = line[0:len(line)-1].lower()
            if(word.isalpha()):
                sw = sw + [word]
            line = f.readline()
    except StopIteration:
        f.close()
    
    return sw

def get_dates():
    (dem_dates,rep_dates) = ({},{})
    # first email date = 1/24
    # most recent date = 6/15
    last_days = [31,29,31,30,31,15] #j,f,m,a,m,j

    for m in range(1,7):
        start = 1
        if(m == 1):
            start = 24
        for d in range(start,last_days[m-1]+1):
            date = str(m)+"/"+str(d)
            dem_dates[date] = 0
            rep_dates[date] = 0

    return (dem_dates,rep_dates)

def define_daily_email_counts():
    (dems_counts,reps_counts) = get_dates()
    dem_data = open('../covid19-dem-emails-and-data.csv','r')
    rep_data = open('../covid19-rep-emails-and-data.csv','r')

    dem_reader = csv.reader(dem_data)
    rep_reader = csv.reader(rep_data)

    row = next(dem_reader)
    row = next(dem_reader)

    try:
        while row:
            
            email_date = row[0][0:row[0].index("2020")-1]

            dems_counts[email_date] += 1

            row = next(dem_reader)
    except ValueError:
        pass
    except StopIteration:
        pass

    row = next(rep_reader)
    row = next(rep_reader)

    try:
        while row:
            
            email_date = row[0][0:row[0].index("2020")-1]

            reps_counts[email_date] += 1

            row = next(rep_reader)
    except ValueError:
        pass
    except StopIteration:
        pass

    dem_data.close()
    rep_data.close()

    return (dems_counts,reps_counts)

def count_ngram(email,date,ngram,frequencies):
    if(len(ngram) == 1):
        for word in email:
            if(ngram == [word]):
                frequencies[date] += 1
    else:
        for word in email:
            if(tuple(ngram) == word):
                frequencies[date] += 1
        
    return frequencies

def occurrences(ngram):
    if(len(ngram) > 3 or len(ngram) < 1):
        print("invalid ngram",ngram)
        return None
    (dems_frequencies,reps_frequencies) = get_dates()
    dem_data = open('../covid19-dem-emails-and-data.csv','r')
    rep_data = open('../covid19-rep-emails-and-data.csv','r')

    dem_reader = csv.reader(dem_data)
    rep_reader = csv.reader(rep_data)

    row = next(dem_reader)
    row = next(dem_reader)
    #count = 0
    try:
        while row:# and count < 20:
            email_date = row[0][0:row[0].index("2020")-1]

            email_words = [w for w in word_tokenize(row[3].lower()) if ('covid19' in w or 'covid-19' in w or (w.isalpha() and not w in stop_words))]
            if(len(ngram) == 2):
                email_words = nltk.bigrams(email_words)
                pass
            elif(len(ngram) == 3):
                email_words = nltk.trigrams(email_words)
                pass
                
            dems_frequencies = count_ngram(email_words,email_date,ngram,dems_frequencies)
            #count += 1
            row = next(dem_reader)
    except StopIteration:
        pass
    except ValueError:
        pass

    row = next(rep_reader)
    row = next(rep_reader)
    #count = 0

    try:
        while row:# and count < 20:
            email_date = row[0][0:row[0].index("2020")-1]

            email_words = [w for w in word_tokenize(row[3].lower()) if ('covid19' in w or 'covid-19' in w or (w.isalpha() and not w in stop_words))]
            if(len(ngram) == 2):
                email_words = nltk.bigrams(email_words)
                pass
            elif(len(ngram) == 3):
                email_words = nltk.trigrams(email_words)
                pass
                
            reps_frequencies = count_ngram(email_words,email_date,ngram,reps_frequencies)
            #count += 1
            row = next(rep_reader)
    except StopIteration:
        pass
    except ValueError:
        pass

    return (dems_frequencies,reps_frequencies)

def visualize(ngram):
    (dems_frequencies,reps_frequencies) = occurrences(ngram)
  
    df = pd.DataFrame({'dem_dates' : list(dems_frequencies.keys()),'dem_counts' : list(dems_frequencies.values()),'rep_dates' : list(reps_frequencies.keys()), 'rep_counts' : list(reps_frequencies.values())})

        
    plt.plot('dem_dates','dem_counts',data=df,color='skyblue',linewidth=2,label='democrat')
    plt.plot('rep_dates','rep_counts',data=df,color='pink',linewidth=2,label='republican')
    plt.title(str("Mentions of "+str(ngram)+" in congressional emails over time"))
    plt.xticks(
        ticks = [0,7,36,67,97,128,143],
        labels = ['1/24','1/31','2/29','3/31','4/30','5/31','6/15']
    )
    
    #George Floyd line May 25
    #ymax = max(list(dems_frequencies.values()) + list(reps_frequencies.values()))
    #plt.vlines(x=122, ymin=0, ymax=ymax, linestyles ="dotted", color ="black")

    plt.legend()  
    plt.show()




if __name__ == '__main__':
    stop_words = update_stopwords()
    (dem_email_counts,rep_email_counts) = define_daily_email_counts()
    # when using these dictionaries, if there are no emails that day, that day is not in the dictionary
    
    # facemask, mask, vaccine, hydroxychloroquine, “Travel warning” prejudice, discrimination, stigma, xenophobia 
    # (May 25 is sort of a dividing line re: George Floyd

    
    visualize(['wuhan','virus'])
    
