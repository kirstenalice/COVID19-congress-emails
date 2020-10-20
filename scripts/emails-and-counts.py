import csv
import re 
import nltk
import requests
import importlib

from dateutil.parser import parse
from nltk.tokenize import word_tokenize
from covid19_over_time import covid19OverTime

'''
    Make a big database with each row is member of congress regardless of if they sent a covid email or not, 
        column for total covid messages sent, dates of messages, and death data appended for each person on last day of month.  
    
    This means that for thoes who send no message will still have legislator and death data, but no message. 
'''

'''
    (just state if Senator) (last day of every month)
Name | State - District | Death Counts by Month | Most Recent death count | Total Emails # | Date of email 1 | email 1 | date of email 2 | email 2 .....
'''

state_abbrev = {"Alabama" : "AL","Alaska" : "AK","Arizona" : "AZ","Arkansas" : "AR","California" : "CA","Colorado" : "CO","Connecticut" : "CT","Delaware" : "DE","Florida" : "FL","Georgia" : "GA","Hawaii" : "HI","Idaho" : "ID","Illinois" : "IL","Indiana" : "IN","Iowa" : "IA","Kansas" : "KS","Kentucky" : "KY","Louisiana" : "LA","Maine" : "ME","Maryland" : "MD","Massachusetts" : "MA","Michigan" : "MI","Minnesota" : "MN","Mississippi" : "MS","Missouri" : "MO","Montana" : "MT","Nebraska" : "NE","Nevada" : "NV","New Hampshire" : "NH","New Jersey" : "NJ","New Mexico" : "NM","New York" : "NY","North Carolina" : "NC","North Dakota" : "ND","Ohio" : "OH","Oklahoma" : "OK","Oregon" : "OR","Pennsylvania" : "PA","Rhode Island" : "RI","South Carolina" : "SC","South Dakota" : "SD","Tennessee" : "TN","Texas" : "TX","Utah" : "UT","Vermont" : "VT","Virginia" : "VA","Washington" : "WA","West Virginia" : "WV","Wisconsin" : "WI","Wyoming" : "WY"}


def get_state_name(abbrev):
    for k,v in state_abbrev.items():
        if v == abbrev:
            return k

# gets a list of last dates in each month, adds most recent date to the end of list 
# dynamic so new months can be included as time goes on
def get_last_dates(cd):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None

    data = open('../CSSEGIS-COVID-19/time_series_covid19_'+ cd +'_US.csv','r')
    data_reader = csv.reader(data)

    headers = next(data_reader)[12:]
    last_dates = []
    prev = [int(d) for d in headers[0].split("/")]

    for date in headers[1:]:
        date_split = [int(d) for d in date.split("/")]
        if(date_split[0] > prev[0]): 
            prev_str = [str(d) for d in prev]
            prev_str = "/".join(prev_str)
            last_dates += [prev_str]
        prev = date_split
    
    last_dates += [headers[len(headers)-1]]
    data.close()
    return last_dates

def get_all_dates(cd):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None

    data = open('../CSSEGIS-COVID-19/time_series_covid19_'+ cd +'_US.csv','r')
    data_reader = csv.reader(data)

    headers = next(data_reader)
    headers = headers[(headers.index('1/22/20')):]
    return headers

# filters out necessary data from hs116-members row
# [Name,Chamber,State,District]
def name_data_filter(row):
    full_name = row[9].lower()
    last_name = full_name[0:full_name.index(",")+1]
    first_name = full_name[full_name.index(","):]
    formatted_name = (first_name + " " + last_name).replace(",","")
    formatted_name_token = word_tokenize(formatted_name.lower())

    suffix = ""
    if('iv' in formatted_name_token):
        suffix = " IV"
    elif('iii' in formatted_name_token):
        suffix = " III"
    elif('jr.' in formatted_name_token):
        suffix = " Jr."
    elif('ii' in formatted_name_token):
        suffix = " II"
    formatted_name_token = [n.capitalize() for n in formatted_name_token if n != 'iv' and n != 'iii' and n != 'jr.' and n != 'ii']

    real_name = " "
    real_name = real_name.join(formatted_name_token) + suffix
    real_name = real_name.replace("( ","(")
    real_name = real_name.replace(" )",")")

    if('-' in real_name):
        index = real_name.index('-')
        real_name = real_name[:index+1] + real_name[index+1].capitalize() + real_name[index+2:]

    if('\'' in real_name):
        index = real_name.index('\'')
        real_name = real_name[:index+1] + real_name[index+1].capitalize() + real_name[index+2:]

    if('Tj Cox' in real_name):
        real_name = real_name.replace("Tj",'TJ')
    elif(' .' in real_name):
        real_name = real_name.replace(" .",".")
    

    for x in range(1,len(real_name)-1):
        if(real_name[x-1] == '.' and real_name[x+1] == '.'):
            real_name = real_name[:x] + real_name[x].capitalize() + real_name[x+1:]
        if(real_name[x-1] == 'M' and real_name[x] == 'c'):
            real_name = real_name[:x+1] + real_name[x+1].capitalize() + real_name[x+2:]

    return [real_name,row[1],str(get_state_name(row[5])),str(row[4])]

# name should be Last, First
# get full row from hs116-members
# copied from name-match.py
def get_congress_data(name):
    
    data = open('../hs116-members.csv',newline='')
    data_reader = csv.reader(data)
    
    # gets column names
    row = next(data_reader)
    # skips to first row of data
    row = next(data_reader)

    try:
        while row:
            repeated_last_names = ["BISHOP",'BLUNT','BROOKS','BROWN','CARTER','CLAY','COLLINS','DAVIS',"DEAN","FLORES",'GARCIA','GONZALEZ','GRAVES','GREEN','HARRIS','HIGGINS','HILL','JOHNSON','JONES','JOYCE','KELLY','KENNEDY','KING','LEE','LEVIN','MALONEY','MURPHY','NEAL','PAUL','PETERS','REED','RICE','ROGERS','ROSE','SCOTT','SMITH','THOMPSON','TORRES','WARREN','WILSON','YOUNG']
            name = name.lower()
            full_name = row[9].lower()

            if('á' in name):
                name = name.replace('á','a')
            if('á' in full_name):
                full_name = full_name.replace('á','a')

            if(len(name) == 0):
                print('name empty: ',name)
                return []

            last_name = re.sub("[-]"," ",name[0:name.index(",")]).split(" ")

            name_token = word_tokenize(re.sub('[-,]'," ",name))
            full_name_token = word_tokenize(re.sub('[-,]'," ",full_name))

            if(set(last_name).issubset(set(full_name_token))):
                is_last_name_dupl = set([name.upper() for name in last_name]).intersection(set(repeated_last_names))
                if(is_last_name_dupl):

                    is_subset = set(name_token).issubset(set(full_name_token))

                    if(is_subset):
                        data.close()                      
                        
                        return row
                else:
                    data.close()
                    return row
            row = next(data_reader)
    except StopIteration:
        data.close()
        print("done")
        return row

def get_covid19_counts(cd,dates,state,district):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None

    if(not state in list(state_abbrev.keys())):
        print("invalid state",state)

    if(district < 0):
        print("There is no district",district,"in",state)
        return None

    for date in dates:
        if(not covid19OverTime.valid_date(cd,date)):
            print("invalid date",date)
            return None

    if(district == 0): # senator
        deaths_over_time = {}
        for date in dates:
            deaths = sum(list(covid19OverTime.get_state_covid19_data(cd,state,date).values()))
            deaths_over_time[date] = deaths
        return deaths_over_time
    else: # house
        deaths_over_time = {}
        for date in dates:
            deaths = covid19OverTime.get_covid19_by_district(cd,state,date)
            if(district > len(deaths)):
                print("no district",district,'in',state)

            deaths_over_time[date] = deaths[district]
        
        return deaths_over_time

# get all emails by congressperson 
# search
def get_all_emails(name):
    row = get_congress_data(name) # from hs116-members
    bioname = row[9]

    dem_file = open("../covid19-dem-emails-and-data.csv","r")
    rep_file = open("../covid19-rep-emails-and-data.csv","r")

    dem_reader = csv.reader(dem_file)
    rep_reader = csv.reader(rep_file)

    # from emails-and-data
    dem_row = next(dem_reader)
    rep_row = next(rep_reader)

    # key = timestamp, value = email contents
    emails = {} 
    try:
        while(dem_row): 
            if(len(dem_row) > 15 and dem_row[14] == bioname):
                emails[dem_row[0]] = dem_row[3]
            dem_row = next(dem_reader)
            if(dem_row[14] > bioname):
                dem_row = None
    except StopIteration:
        pass
    try:   
        while(rep_row): 
            if(len(rep_row) > 15 and rep_row[14] == bioname):
                emails[rep_row[0]] = rep_row[3]
            rep_row = next(rep_reader)
            if(rep_row[14] > bioname):
                rep_row = None
    except StopIteration:
        pass
    dem_file.close()
    rep_file.close()
    return emails

# function that writes it all to a csv
def create_email_table(cd,dates):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None

    for date in dates:
        if(not covid19OverTime.valid_date(cd,date)):
            print("invalid date",date)
            return None

    member_data = open('../hs116-members.csv','r')
    reader = csv.reader(member_data)

    row = next(reader)

    file = open('../emails-and-daily-'+cd+'.csv','w',newline='')

    writer = csv.writer(file)

    email_headers = []
    for x in range(1,128):
        email_headers += ['Date '+str(x)]
        email_headers += ['Email '+str(x)]

    headers = ['Name'] + row + dates + ['Total Emails'] + email_headers
    writer.writerow(headers)

    row = next(reader)
    #count = 0
    try:
        while row: # and count < 5:
            nom_data = name_data_filter(get_congress_data(row[9]))
            print(nom_data[0],nom_data[2])
            covid19_data = get_covid19_counts(cd,dates,nom_data[2],int(nom_data[3])) # state,district

            emails = get_all_emails(row[9])

            emails_data = []
            new_row = [nom_data[0]] + row + list(covid19_data.values())
            if(not emails == None):
                for date,email in emails.items():
                    emails_data += [date,email]

                new_row += ([len(emails)] + emails_data)
            else:
                new_row += [0]
            writer.writerow(new_row)

            row = next(reader)
            #count += 1
    except StopIteration:
        print("DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    
    file.close()
    member_data.close()
    
if __name__ == '__main__':
    #print("Matching congresspeople with death data...")
    
    #print(get_congress_data("CRUZ, Rafael Edward (Ted)"))
    #print(name_data_filter(get_congress_data("CRUZ, Rafael Edward (Ted)")))
    #print(get_monthly_covid19_counts("Texas",0))
    #print(len(get_all_emails("CRUZ, Rafael Edward (Ted)")))
    #print(len(get_all_emails("bernie sanders")))
    
    # Downloads most recent version of Johns Hopkins COVID19 death data
    '''
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
    r = requests.get(url, allow_redirects=True)

    f = open('../CSSEGIS-COVID-19/time_series_covid19_deaths_US.csv', 'wb')
    f.write(r.content)
    f.close()

    
    #print(name_data_filter(get_congress_data("O'HALLERAN, Thomas C.")))
    
    create_email_table()

    #print(get_all_dates())
    '''

    cd = 'deaths'
    
    covid19OverTime.update_data(cd)
    create_email_table(cd,get_all_dates(cd))
    #print(len(get_all_emails("WATSON-COLEMAN, Bonnie")))

