# uni/bi/trigram frequency
# graph ngram frequency over time by party

import csv
import re 
import nltk
import matplotlib.pyplot as plt

from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from nltk.util import ngrams
from covid19_over_time import covid19OverTime

'''
    produce multiple files for given Month:
        - death counts for all districts in Month
        - unigrams for dem/rep in that month
        - bigrams for dem/rep in that month
        - trigrams for dem/rep in that month
        - create new folder for all these files to go in: frequencies/month-2020/files
'''

stop_words = ""
irrelevant_words = ['covid','corona','open','plain','text','version','united','states','dear','friend','would','like']

dem_email_counts = {1: 13, 2: 105, 3: 1054, 4: 1173, 5: 913, 6: 268}
rep_email_counts = {1: 13, 2: 94, 3: 994, 4: 1054, 5: 860, 6: 274}

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

def monthstring(month):
    monthstring = ""
    if(month == 1):
        monthstring = 'january'
    elif(month == 2):
        monthstring = 'february'
    elif(month == 3):
        monthstring = 'march'
    elif(month == 4):
        monthstring = 'april'
    elif(month == 5):
        monthstring = 'may'
    elif(month == 6):
        monthstring = 'june'
    
    return monthstring

# create file of case counts by month
def case_counts(month):
    update_data('confirmed')
    death_data = open('../CSSEGIS-COVID-19/time_series_covid19_confirmed_US.csv','r')

    dd_reader = csv.reader(death_data)

    headers = next(dd_reader)
    start_index = 0
    end_index = 0

    # rmr to change for new months if you get new emails
    if(month == 1):
        start_index = headers.index('1/22/20')
        end_index = headers.index('2/1/20')
    else:
        start_index = headers.index(str(month)+'/1/20')
        end_index = headers.index(str(month+1)+'/1/20') # noninclusive

    dates = headers[start_index:end_index]
    
    covid19OverTime.get_all_covid19_by_district_over_time('deaths',dates[0],dates[len(dates)-1])
    death_data.close()

# create file of death counts by month
def death_counts(month):
    update_data('deaths')
    death_data = open('../CSSEGIS-COVID-19/time_series_covid19_deaths_US.csv','r')

    dd_reader = csv.reader(death_data)

    headers = next(dd_reader)
    start_index = 0
    end_index = 0

    # rmr to change for new months if you get new emails
    if(month == 1):
        start_index = headers.index('1/22/20')
        end_index = headers.index('2/1/20')
    else:
        start_index = headers.index(str(month)+'/1/20')
        end_index = headers.index(str(month+1)+'/1/20') # noninclusive

    dates = headers[start_index:end_index]
    
    covid19OverTime.get_all_covid19_by_district_over_time('deaths',dates[0],dates[len(dates)-1])
    death_data.close()

def count_words(email,frequencies):
    for word in email:
        if(word in frequencies):
            frequencies[word] += 1
        else:
            frequencies[word] = 1

    return frequencies

# month must be a number 1-6
def unigrams(month):
    dem_frequencies = {}
    rep_frequencies = {}

    dem_data = open('../covid19-dem-emails-and-data.csv','r')

    dem_reader = csv.reader(dem_data)
    row = next(dem_reader)

    row = next(dem_reader)
    try:
        while row:
            email_date = row[0]
            email_month = int(email_date[0:email_date.index('/')])
            if(month == 0 or email_month == month):
                email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
                dem_frequencies = count_words(email,dem_frequencies)
            elif(email_month < month):
                break
            row = next(dem_reader)
    except StopIteration:
        pass

    dem_data.close()
    # print("dem done")
    rep_data = open('../covid19-rep-emails-and-data.csv','r')

    rep_reader = csv.reader(rep_data)
    row = next(rep_reader)

    row = next(rep_reader)
    try:
        while row:
            email_date = row[0]
            email_month = int(email_date[0:email_date.index('/')])
            if(month == 0 or email_month == month):
                email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
                rep_frequencies = count_words(email,rep_frequencies)
            elif(email_month < month):
                break
            row = next(rep_reader)
    except StopIteration:
        pass

    rep_data.close()
    
    dem_frequencies = {k : v for k,v in sorted(dem_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}
    rep_frequencies = {k : v for k,v in sorted(rep_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}

    with open('../frequencies/'+ monthstring(month) +'/dem-'+str(month)+'-unigrams.txt','w') as file:
        for k,v in dem_frequencies.items():
            file.write(k + ": " + str(v) + "\n")
        
        file.close()
    
    with open('../frequencies/'+ monthstring(month) +'/rep-'+str(month)+'-unigrams.txt','w') as file:
        for k,v in rep_frequencies.items():
            file.write(k + ": " + str(v) + "\n")
        
        file.close()

# month must be a number 1-6
def bigrams(month):
    dem_frequencies = {}
    rep_frequencies = {}

    dem_data = open('../covid19-dem-emails-and-data.csv','r')

    dem_reader = csv.reader(dem_data)
    row = next(dem_reader)

    row = next(dem_reader)
    try:
        while row:
            email_date = row[0]
            email_month = int(email_date[0:email_date.index('/')])
            if(month == 0 or email_month == month):
                email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
                dem_frequencies = count_words(nltk.bigrams(email),dem_frequencies)
            elif(email_month < month):
                break
            row = next(dem_reader)
    except StopIteration:
        pass

    dem_data.close()
    # print("dem done")
    rep_data = open('../covid19-rep-emails-and-data.csv','r')

    rep_reader = csv.reader(rep_data)
    row = next(rep_reader)

    row = next(rep_reader)
    try:
        while row:
            email_date = row[0]
            email_month = int(email_date[0:email_date.index('/')])
            if(month == 0 or email_month == month):
                email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
                rep_frequencies = count_words(nltk.bigrams(email),rep_frequencies)
            elif(email_month < month):
                break
            row = next(rep_reader)
    except StopIteration:
        pass

    rep_data.close()
    
    dem_frequencies = {k : v for k,v in sorted(dem_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}
    rep_frequencies = {k : v for k,v in sorted(rep_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}

    with open('../frequencies/'+ monthstring(month) +'/dem-'+str(month)+'-bigrams.txt','w') as file:
        for k, v in dem_frequencies.items():
            file.write("(" + k[0] + ", " + k[1] + ") : " + str(v) + "\n")
        
        file.close()
    
    with open('../frequencies/'+ monthstring(month) +'/rep-'+str(month)+'-bigrams.txt','w') as file:
        for k, v in rep_frequencies.items():
            file.write("(" + k[0] + ", " + k[1] + ") : " + str(v) + "\n")
        
        file.close()

# month must be a number 1-6
def trigrams(month):
    dem_frequencies = {}
    rep_frequencies = {}

    dem_data = open('../covid19-dem-emails-and-data.csv','r')

    dem_reader = csv.reader(dem_data)
    row = next(dem_reader)

    row = next(dem_reader)
    try:
        while row:
            email_date = row[0]
            email_month = int(email_date[0:email_date.index('/')])
            if(month == 0 or email_month == month):
                email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
                dem_frequencies = count_words(nltk.trigrams(email),dem_frequencies)
            elif(email_month < month):
                break
            row = next(dem_reader)
    except StopIteration:
        pass

    dem_data.close()
    # print("dem done")
    rep_data = open('../covid19-rep-emails-and-data.csv','r')

    rep_reader = csv.reader(rep_data)
    row = next(rep_reader)

    row = next(rep_reader)
    try:
        while row:
            email_date = row[0]
            email_month = int(email_date[0:email_date.index('/')])
            if(month == 0 or email_month == month):
                email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
                rep_frequencies = count_words(nltk.trigrams(email),rep_frequencies)
            elif(email_month < month):
                break
            row = next(rep_reader)
    except StopIteration:
        pass

    rep_data.close()
    
    dem_frequencies = {k : v for k,v in sorted(dem_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}
    rep_frequencies = {k : v for k,v in sorted(rep_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}

    with open('../frequencies/'+ monthstring(month) +'/dem-'+str(month)+'-trigrams.txt','w') as file:
        for k, v in dem_frequencies.items():
            file.write("(" + k[0] + ", " + k[1] + ", " + k[2] + ") : " + str(v) + "\n")
        
        file.close()
    
    with open('../frequencies/'+ monthstring(month) +'/rep-'+str(month)+'-trigrams.txt','w') as file:
        for k, v in rep_frequencies.items():
            file.write("(" + k[0] + ", " + k[1] + ", " + k[2] + ") : " + str(v) + "\n")
        
        file.close()

def all_unigrams():
    dem_frequencies = {}
    rep_frequencies = {}

    dem_data = open('../covid19-dem-emails-and-data.csv','r')

    dem_reader = csv.reader(dem_data)
    row = next(dem_reader)

    row = next(dem_reader)
    try:
        while row:
            email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
            dem_frequencies = count_words(email,dem_frequencies)

            row = next(dem_reader)
    except StopIteration:
        pass

    dem_data.close()
    # print("dem done")
    rep_data = open('../covid19-rep-emails-and-data.csv','r')

    rep_reader = csv.reader(rep_data)
    row = next(rep_reader)

    row = next(rep_reader)
    try:
        while row:
            email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
            rep_frequencies = count_words(email,rep_frequencies)

            row = next(rep_reader)
    except StopIteration:
        pass

    rep_data.close()
    
    dem_frequencies = {k : v for k,v in sorted(dem_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}
    rep_frequencies = {k : v for k,v in sorted(rep_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}

    with open('../frequencies/all/dem-unigrams.txt','w') as file:
        for k,v in dem_frequencies.items():
            file.write(k + ": " + str(v) + "\n")
        
        file.close()
    
    with open('../frequencies/all/rep-unigrams.txt','w') as file:
        for k,v in rep_frequencies.items():
            file.write(k + ": " + str(v) + "\n")
        
        file.close()

def all_bigrams():
    dem_frequencies = {}
    rep_frequencies = {}

    dem_data = open('../covid19-dem-emails-and-data.csv','r')

    dem_reader = csv.reader(dem_data)
    row = next(dem_reader)

    row = next(dem_reader)
    try:
        while row:
            email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
            dem_frequencies = count_words(nltk.bigrams(email),dem_frequencies)
         
            row = next(dem_reader)
    except StopIteration:
        pass

    dem_data.close()
    # print("dem done")
    rep_data = open('../covid19-rep-emails-and-data.csv','r')

    rep_reader = csv.reader(rep_data)
    row = next(rep_reader)

    row = next(rep_reader)
    try:
        while row:
            email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
            rep_frequencies = count_words(nltk.bigrams(email),rep_frequencies)

            row = next(rep_reader)
    except StopIteration:
        pass

    rep_data.close()
    
    dem_frequencies = {k : v for k,v in sorted(dem_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}
    rep_frequencies = {k : v for k,v in sorted(rep_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}

    with open('../frequencies/all/dem-bigrams.txt','w') as file:
        for k, v in dem_frequencies.items():
            file.write("(" + k[0] + ", " + k[1] + ") : " + str(v) + "\n")
        
        file.close()
    
    with open('../frequencies/all/rep-bigrams.txt','w') as file:
        for k, v in rep_frequencies.items():
            file.write("(" + k[0] + ", " + k[1] + ") : " + str(v) + "\n")
        
        file.close()

def all_trigrams():
    dem_frequencies = {}
    rep_frequencies = {}

    dem_data = open('../covid19-dem-emails-and-data.csv','r')

    dem_reader = csv.reader(dem_data)
    row = next(dem_reader)

    row = next(dem_reader)
    try:
        while row:
            email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
            dem_frequencies = count_words(nltk.trigrams(email),dem_frequencies)

            row = next(dem_reader)
    except StopIteration:
        pass

    dem_data.close()
    # print("dem done")
    rep_data = open('../covid19-rep-emails-and-data.csv','r')

    rep_reader = csv.reader(rep_data)
    row = next(rep_reader)

    row = next(rep_reader)
    try:
        while row:
            email = [w for w in word_tokenize(row[3].lower()) if (w.isalpha() and not w in stop_words)] # remove punctuation and stopwords
            rep_frequencies = count_words(nltk.trigrams(email),rep_frequencies)

            row = next(rep_reader)
    except StopIteration:
        pass

    rep_data.close()
    
    dem_frequencies = {k : v for k,v in sorted(dem_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}
    rep_frequencies = {k : v for k,v in sorted(rep_frequencies.items(),key = lambda item: item[1],reverse=True) if v > 1}

    with open('../frequencies/all/dem-trigrams.txt','w') as file:
        for k, v in dem_frequencies.items():
            file.write("(" + k[0] + ", " + k[1] + ", " + k[2] + ") : " + str(v) + "\n")
        
        file.close()
    
    with open('../frequencies/all/rep-trigrams.txt','w') as file:
        for k, v in rep_frequencies.items():
            file.write("(" + k[0] + ", " + k[1] + ", " + k[2] + ") : " + str(v) + "\n")
        
        file.close()

def visualize(month):
    if(month > 6 or month < 0):
        print("invalid month",month)
    elif(month == 0): # all time
        fig,axs = plt.subplots(3,2)

        fig.suptitle("Most Common Phrases in Democrat and Republican Emails")
        
        file = open('../frequencies/all/dem-unigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()
            
        axs[0,0].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='skyblue')
        axs[0,0].invert_yaxis()

        rects = axs[0,0].patches

        for rect, p in zip(rects,phrases):
            axs[0,0].text(400,rect.get_y()+0.8,str(p))

        
        file = open('../frequencies/all/dem-bigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()

        axs[1,0].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='skyblue')

        axs[1,0].invert_yaxis()

        rects = axs[1,0].patches

        for rect, p in zip(rects,phrases):
            axs[1,0].text(100,rect.get_y()+0.8,str(p),size=9)
            
        
        file = open('../frequencies/all/dem-trigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()

        axs[2,0].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='skyblue')

        axs[2,0].invert_yaxis()

        rects = axs[2,0].patches

        for rect, p in zip(rects,phrases):
            axs[2,0].text(10,rect.get_y()+0.8,str(p),size=8)

        file = open('../frequencies/all/rep-unigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()

        axs[0,1].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='pink')
        axs[0,1].invert_yaxis()

        rects = axs[0,1].patches

        for rect, p in zip(rects,phrases):
            axs[0,1].text(400,rect.get_y()+0.8,str(p))

        file = open('../frequencies/all/rep-bigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()

        axs[1,1].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='pink')

        axs[1,1].invert_yaxis()

        rects = axs[1,1].patches

        for rect, p in zip(rects,phrases):
            axs[1,1].text(100,rect.get_y()+0.8,str(p),size=9)
            
        
        file = open('../frequencies/all/rep-trigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()

        axs[2,1].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='pink')

        axs[2,1].invert_yaxis()

        rects = axs[2,1].patches

        for rect, p in zip(rects,phrases):
            axs[2,1].text(10,rect.get_y()+0.8,str(p),size=8)

        
        file.close()
        plt.show()
    elif(month >= 1 and month <= 6):
        fig,axs = plt.subplots(3,2)

        fig.suptitle("Most Common Phrases in Democrat and Republican Emails during " + monthstring(month).capitalize() + " 2020")
        
        file = open('../frequencies/'+monthstring(month)+'/dem-'+str(month)+'-unigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()
            
        axs[0,0].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='skyblue')
        axs[0,0].invert_yaxis()

        rects = axs[0,0].patches

        for rect, p in zip(rects,phrases):
            axs[0,0].text(1,rect.get_y()+0.8,str(p))

        
        file = open('../frequencies/'+monthstring(month)+'/dem-'+str(month)+'-bigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            
            bigram = re.sub('[() ]',"",split_line[0]).split(",")
            if(len(bigram[0]) < 2 or len(bigram[1]) < 2):
                flag = True
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()

        axs[1,0].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='skyblue')

        axs[1,0].invert_yaxis()

        rects = axs[1,0].patches

        for rect, p in zip(rects,phrases):
            axs[1,0].text(1,rect.get_y()+0.8,str(p),size=9)
            
        
        file = open('../frequencies/'+monthstring(month)+'/dem-'+str(month)+'-trigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            
            trigram = re.sub('[() ]',"",split_line[0]).split(",")
            if(len(trigram[0]) < 2 or len(trigram[1]) < 2 or len(trigram[2]) < 2):
                flag = True
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()

        axs[2,0].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='skyblue')

        axs[2,0].invert_yaxis()

        rects = axs[2,0].patches

        for rect, p in zip(rects,phrases):
            axs[2,0].text(1,rect.get_y()+0.8,str(p),size=8)

        file = open('../frequencies/'+monthstring(month)+'/rep-'+str(month)+'-unigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()

        axs[0,1].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='pink')
        axs[0,1].invert_yaxis()

        rects = axs[0,1].patches

        for rect, p in zip(rects,phrases):
            axs[0,1].text(1,rect.get_y()+0.8,str(p))

        file = open('../frequencies/'+monthstring(month)+'/rep-'+str(month)+'-bigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            
            bigram = re.sub('[() ]',"",split_line[0]).split(",")
            if(len(bigram[0]) < 2 or len(bigram[1]) < 2):
                flag = True
                print(bigram)
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()

        axs[1,1].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='pink')

        axs[1,1].invert_yaxis()

        rects = axs[1,1].patches

        for rect, p in zip(rects,phrases):
            axs[1,1].text(1,rect.get_y()+0.8,str(p),size=9)
            
        
        file = open('../frequencies/'+monthstring(month)+'/rep-'+str(month)+'-trigrams.txt','r')
        x = 0
        line = file.readline()
        phrases = []
        counts = []
        while line and x < 10:
            split_line = line[0:len(line)-1].split(": ")
            flag = False
            for word in irrelevant_words:
                if(word in split_line[0]):
                    flag = True
                    break
            
            trigram = re.sub('[() ]',"",split_line[0]).split(",")
            if(len(trigram[0]) < 2 or len(trigram[1]) < 2 or len(trigram[2]) < 2):
                flag = True
            if(not flag and not int(split_line[1]) in counts):
                # print(split_line,"!!!")
                phrases += [split_line[0]]
                counts += [int(split_line[1])]
                x += 1
            line = file.readline()

        axs[2,1].barh(y=[str(c) for c in counts],width=counts,height=0.8,color='pink')

        axs[2,1].invert_yaxis()

        rects = axs[2,1].patches

        for rect, p in zip(rects,phrases):
            axs[2,1].text(1,rect.get_y()+0.8,str(p),size=8)

        
        file.close()
        plt.show()


if __name__ == '__main__':
    stop_words = update_stopwords()

    visualize(0)


