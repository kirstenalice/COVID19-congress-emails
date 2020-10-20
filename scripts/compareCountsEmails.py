import csv
import re 
import nltk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from nltk.util import ngrams
from covid19_over_time import covid19OverTime

'''

compare deaths/cases vs email counts

'''
def visualize_deaths_vs_emails():
    dem_reps_deaths_emails, rep_reps_deaths_emails = {},{}
    dem_sens_deaths_emails, rep_sens_deaths_emails = {},{}

    data = open('../emails-and-daily-deaths.csv','r')
    reader = csv.reader(data)
    row = next(reader)

    # most recent emails
    last_deaths_index = row.index('6/15/20')
    emails_total_index = row.index('Total Emails')
    party_index = row.index('party_code')
    district_index = row.index('district_code')
    state_index = row.index('state_abbrev')

    x = 0
    try:
        row = next(reader)
        while row and x < 535:
            if(int(row[district_index]) != 0): # representatives
                if(int(row[party_index]) == 200): # republicans
                    try:    
                        # row[0] = Name
                        rep_reps_deaths_emails[str(row[state_index])+"-"+str(row[district_index])] = (int(row[last_deaths_index]),int(row[emails_total_index]))
                    except ValueError:
                        rep_reps_deaths_emails[str(row[state_index])+"-"+str(row[district_index])] = (0,0)
                else: # democrats
                    try:    
                        # row[0] = Name
                        dem_reps_deaths_emails[str(row[state_index])+"-"+str(row[district_index])] = (int(row[last_deaths_index]),int(row[emails_total_index]))
                    except ValueError:
                        dem_reps_deaths_emails[str(row[state_index])+"-"+str(row[district_index])] = (0,0)
            else: # senators
                if(int(row[party_index]) == 200): # republicans
                    try:
                        # row[0] = Name
                        rep_sens_deaths_emails[str(row[state_index])] = (int(row[last_deaths_index]),int(row[emails_total_index]))
                    except ValueError:
                        rep_sens_deaths_emails[str(row[state_index])] = (0,0)
                else: # democrats
                    try:
                        # row[0] = Name
                        dem_sens_deaths_emails[str(row[state_index])] = (int(row[last_deaths_index]),int(row[emails_total_index]))
                    except ValueError:
                        dem_sens_deaths_emails[str(row[state_index])] = (0,0)
            row = next(reader)
            x += 1

    except StopIteration:
        data.close()
        print('done')

    dem_reps_names = list(dem_reps_deaths_emails.keys())
    dem_sens_names = list(dem_sens_deaths_emails.keys())
    rep_reps_names = list(rep_reps_deaths_emails.keys())
    rep_sens_names = list(rep_sens_deaths_emails.keys())

    fig,axs = plt.subplots(2,2,figsize=(9,9))

    deaths = [death for (death,email) in list(dem_sens_deaths_emails.values())]
    emails = [email for (death,email) in list(dem_sens_deaths_emails.values())]

    axs[0,0].scatter(deaths,emails,s=4,color='blue')
    axs[0,0].set_title('Democrat Senators')
    axs[0,0].set_xlabel('deaths')
    axs[0,0].set_ylabel('email count')
    labelled = []
    for x in range(0,len(dem_sens_names)):
        if((not (deaths[x],emails[x]) in labelled) and (deaths[x] > 7000 or emails[x] > 40)):
            axs[0,0].text(deaths[x],emails[x],dem_sens_names[x])
            labelled += [(deaths[x],emails[x])]


    deaths = [death for (death,email) in list(dem_reps_deaths_emails.values())]
    emails = [email for (death,email) in list(dem_reps_deaths_emails.values())]

    axs[0,1].scatter(deaths,emails,s=4,color='blue')
    axs[0,1].set_title('Democrat Representatives')
    axs[0,1].set_xlabel('deaths')
    axs[0,1].set_ylabel('email count')
    labelled = []
    for x in range(0,len(dem_reps_names)):
        if((not (deaths[x],emails[x]) in labelled) and (deaths[x] > 2000 or emails[x] > 40)):
            axs[0,1].text(deaths[x],emails[x],dem_reps_names[x])
            labelled += [(deaths[x],emails[x])]

    deaths = [death for (death,email) in list(rep_sens_deaths_emails.values())]
    emails = [email for (death,email) in list(rep_sens_deaths_emails.values())]

    axs[1,0].scatter(deaths,emails,s=4,color='red')
    axs[1,0].set_title('Republican Senators')
    axs[1,0].set_xlabel('deaths')
    axs[1,0].set_ylabel('email count')
    labelled = []
    for x in range(0,len(rep_sens_names)):
        if((not (deaths[x],emails[x]) in labelled) and (deaths[x] > 1000 or emails[x] > 12)):
            axs[1,0].text(deaths[x],emails[x],rep_sens_names[x])
            labelled += [(deaths[x],emails[x])]

    deaths = [death for (death,email) in list(rep_reps_deaths_emails.values())]
    emails = [email for (death,email) in list(rep_reps_deaths_emails.values())]

    axs[1,1].scatter(deaths,emails,s=4,color='red')
    axs[1,1].set_title('Republican Representatives')
    axs[1,1].set_xlabel('deaths')
    axs[1,1].set_ylabel('email count')
    labelled = []
    for x in range(0,len(rep_reps_names)):
        if((not (deaths[x],emails[x]) in labelled) and (deaths[x] > 400 or emails[x] > 80)):
            axs[1,1].text(deaths[x],emails[x],rep_reps_names[x])
            labelled += [(deaths[x],emails[x])]

    plt.tight_layout()
    plt.show()

def visualize_cases_vs_emails():
    dem_reps_deaths_emails, rep_reps_deaths_emails = {},{}
    dem_sens_deaths_emails, rep_sens_deaths_emails = {},{}

    data = open('../emails-and-daily-confirmed.csv','r')
    reader = csv.reader(data)
    row = next(reader)

    # most recent emails
    last_deaths_index = row.index('6/15/20')
    emails_total_index = row.index('Total Emails')
    party_index = row.index('party_code')
    district_index = row.index('district_code')
    state_index = row.index('state_abbrev')

    x = 0
    try:
        row = next(reader)
        while row and x < 535:
            if(int(row[district_index]) != 0): # representatives
                if(int(row[party_index]) == 200): # republicans
                    try:    
                        # row[0] = Name
                        rep_reps_deaths_emails[str(row[state_index])+"-"+str(row[district_index])] = (int(row[last_deaths_index]),int(row[emails_total_index]))
                    except ValueError:
                        rep_reps_deaths_emails[str(row[state_index])+"-"+str(row[district_index])] = (0,0)
                else: # democrats
                    try:    
                        # row[0] = Name
                        dem_reps_deaths_emails[str(row[state_index])+"-"+str(row[district_index])] = (int(row[last_deaths_index]),int(row[emails_total_index]))
                    except ValueError:
                        dem_reps_deaths_emails[str(row[state_index])+"-"+str(row[district_index])] = (0,0)
            else: # senators
                if(int(row[party_index]) == 200): # republicans
                    try:
                        # row[0] = Name
                        rep_sens_deaths_emails[str(row[state_index])] = (int(row[last_deaths_index]),int(row[emails_total_index]))
                    except ValueError:
                        rep_sens_deaths_emails[str(row[state_index])] = (0,0)
                else: # democrats
                    try:
                        # row[0] = Name
                        dem_sens_deaths_emails[str(row[state_index])] = (int(row[last_deaths_index]),int(row[emails_total_index]))
                    except ValueError:
                        dem_sens_deaths_emails[str(row[state_index])] = (0,0)
            row = next(reader)
            x += 1

    except StopIteration:
        data.close()
        print('done')

    dem_reps_names = list(dem_reps_deaths_emails.keys())
    dem_sens_names = list(dem_sens_deaths_emails.keys())
    rep_reps_names = list(rep_reps_deaths_emails.keys())
    rep_sens_names = list(rep_sens_deaths_emails.keys())

    fig,axs = plt.subplots(2,2,figsize=(9,9))

    deaths = [death for (death,email) in list(dem_sens_deaths_emails.values())]
    emails = [email for (death,email) in list(dem_sens_deaths_emails.values())]

    axs[0,0].scatter(deaths,emails,s=4,color='blue')
    axs[0,0].set_title('Democrat Senators')
    axs[0,0].set_xlabel('deaths')
    axs[0,0].set_ylabel('email count')
    labelled = []
    for x in range(0,len(dem_sens_names)):
        if((not (deaths[x],emails[x]) in labelled) and (deaths[x] > 100000 or emails[x] > 20)):
            axs[0,0].text(deaths[x],emails[x],dem_sens_names[x])
            labelled += [(deaths[x],emails[x])]


    deaths = [death for (death,email) in list(dem_reps_deaths_emails.values())]
    emails = [email for (death,email) in list(dem_reps_deaths_emails.values())]

    axs[0,1].scatter(deaths,emails,s=4,color='blue')
    axs[0,1].set_title('Democrat Representatives')
    axs[0,1].set_xlabel('deaths')
    axs[0,1].set_ylabel('email count')
    labelled = []
    for x in range(0,len(dem_reps_names)):
        if((not (deaths[x],emails[x]) in labelled) and (deaths[x] > 25000 or emails[x] > 38)):
            axs[0,1].text(deaths[x],emails[x],dem_reps_names[x])
            labelled += [(deaths[x],emails[x])]

    deaths = [death for (death,email) in list(rep_sens_deaths_emails.values())]
    emails = [email for (death,email) in list(rep_sens_deaths_emails.values())]

    axs[1,0].scatter(deaths,emails,s=4,color='red')
    axs[1,0].set_title('Republican Senators')
    axs[1,0].set_xlabel('deaths')
    axs[1,0].set_ylabel('email count')
    labelled = []
    for x in range(0,len(rep_sens_names)):
        if((not (deaths[x],emails[x]) in labelled) and (deaths[x] > 25000 or emails[x] > 15)):
            axs[1,0].text(deaths[x],emails[x],rep_sens_names[x])
            labelled += [(deaths[x],emails[x])]

    deaths = [death for (death,email) in list(rep_reps_deaths_emails.values())]
    emails = [email for (death,email) in list(rep_reps_deaths_emails.values())]

    axs[1,1].scatter(deaths,emails,s=4,color='red')
    axs[1,1].set_title('Republican Representatives')
    axs[1,1].set_xlabel('deaths')
    axs[1,1].set_ylabel('email count')
    labelled = []
    for x in range(0,len(rep_reps_names)):
        if((not (deaths[x],emails[x]) in labelled) and (deaths[x] > 9000 or emails[x] > 60)):
            axs[1,1].text(deaths[x],emails[x],rep_reps_names[x])
            labelled += [(deaths[x],emails[x])]

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    #visualize_cases_vs_emails()
    visualize_deaths_vs_emails()