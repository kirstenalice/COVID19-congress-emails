import csv
import re 
import nltk
import requests
import os

from dateutil.parser import parse
from nltk.tokenize import word_tokenize

'''
    get death count by congressional district
    start with all deaths, then once the algorithm is done break down to time frames
'''

'''
    CSSEGIC-COVID-19 folder = covid-19 death data over time by county
    deaths_by_district = results folder, currently csv for each state
    states_and_distrcts = county to district population and afact data
'''
state_abbrev = {"Alabama" : "AL","Alaska" : "AK","Arizona" : "AZ","Arkansas" : "AR","California" : "CA","Colorado" : "CO","Connecticut" : "CT","Delaware" : "DE","Florida" : "FL","Georgia" : "GA","Hawaii" : "HI","Idaho" : "ID","Illinois" : "IL","Indiana" : "IN","Iowa" : "IA","Kansas" : "KS","Kentucky" : "KY","Louisiana" : "LA","Maine" : "ME","Maryland" : "MD","Massachusetts" : "MA","Michigan" : "MI","Minnesota" : "MN","Mississippi" : "MS","Missouri" : "MO","Montana" : "MT","Nebraska" : "NE","Nevada" : "NV","New Hampshire" : "NH","New Jersey" : "NJ","New Mexico" : "NM","New York" : "NY","North Carolina" : "NC","North Dakota" : "ND","Ohio" : "OH","Oklahoma" : "OK","Oregon" : "OR","Pennsylvania" : "PA","Rhode Island" : "RI","South Carolina" : "SC","South Dakota" : "SD","Tennessee" : "TN","Texas" : "TX","Utah" : "UT","Vermont" : "VT","Virginia" : "VA","Washington" : "WA","West Virginia" : "WV","Wisconsin" : "WI","Wyoming" : "WY"}
not_counties = {}

def update_data(cd):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None
    # Downloads most recent version of Johns Hopkins covid19 death data
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_'+ cd +'_US.csv'
    r = requests.get(url, allow_redirects=True)

    
    f = open('../CSSEGIS-COVID-19/time_series_covid19_'+ cd + '_US-original.csv','wb')
    f.write(r.content)
    f.close()
    
    f = open('../CSSEGIS-COVID-19/time_series_covid19_'+ cd + '_US-original.csv','r')

    with open('../CSSEGIS-COVID-19/time_series_covid19_'+ cd + '_US.csv', 'w',newline="") as out:
        try:
            writer = csv.writer(out)
            reader = csv.reader(f)
            row = next(reader)
            index = row.index('Province_State')

            writer.writerow(row)
            row = next(reader)
            while row:
                if(row[6] in list(state_abbrev.keys())):
                    writer.writerow(row)
                row = next(reader)
        except StopIteration:
            pass
            
        out.close()
    f.close()
    if(os.path.exists('../CSSEGIS-COVID-19/time_series_covid19_'+ cd + '_US-original.csv')):
        os.remove('../CSSEGIS-COVID-19/time_series_covid19_'+ cd + '_US-original.csv')

# returns True if date is valid calendar date, ex: 6/45/20 -> False, 4/12/20 -> True
#   and if the date falls in the range 1/22/20 - whatever the most updated date in time_......csv
def valid_date(cd,date):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None
    # reader for the csv file
    covid19_by_county = open('../CSSEGIS-COVID-19/time_series_covid19_' + cd + '_US.csv','r')
    covid19_by_county_reader = csv.reader(covid19_by_county)
    # column headers    
    row = next(covid19_by_county_reader)

    recent = row[len(row)-1]
    recent_date = [int(r) for r in recent.split("/")]

    try:
        parse(date)
    except ValueError:
        covid19_by_county.close()
        return False
    date_split = [int(d) for d in date.split("/")]
    if(date_split[0] > recent_date[0] or date_split[0] < 1 or (date_split[0] == recent_date[0] and date_split[1] > recent_date[1]) or (date_split[0] == 1 and date_split[1] < 22) or date_split[2] != 20):
        print("invalid date: ",date)
        covid19_by_county.close()
        return False
    covid19_by_county.close()
    return True

# returns list of dates between start_date and end_date as strings in MM/DD/YY form
def dates_between(cd,start_date,end_date):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None
    if(not valid_date(cd,start_date) or not valid_date(cd,end_date)):
        print("invalid dates",start_date,end_date)
        return None
    
    dates = []
    # get time.....csv and find column headers that match start and end, avoids converting from string to date to string again
    covid19_by_county = open('../CSSEGIS-COVID-19/time_series_covid19_' + cd + '_US.csv','r')
    covid19_by_county_reader = csv.reader(covid19_by_county)
    # column headers    
    row = next(covid19_by_county_reader)
    covid19_by_county.close()

    start_index = 0
    end_index = 0

    start_date_split = [int(s) for s in start_date.split("/")]
    end_date_split = [int(e) for e in end_date.split("/")]
    
    for x in range(12,len(row)):
        date = [int(d) for d in row[x].split("/")]
        if(date == start_date_split):
            start_index = x
        elif(date == end_date_split):
            end_index = x

        if(start_index > 0 and end_index > 0):
            if(start_index > end_index):
                print("end date is chronologically before start date",start_date,end_date)
                covid19_by_county.close()
                return None
            else: 
                break

    for x in range(start_index,end_index+1):
        dates += [row[x]]
    covid19_by_county.close()
    return dates

# state must be full name ex: "New Jersey" NOT "NJ"
# date must be no earlier than 1/22/20 and no later than 6/23/20 (or the most recent date w data)
# returns dictionary of state's covid19 death data by county for a single date in time
# {"County State" : county covid-deaths}, ex. {"Atlantic NJ", ###}, returns None if parameters are invalid
# NOTE: sometimes the total deaths from this function are different than total deaths in get_covid19_by_district because there are rows with deaths not based in a county, some for a city etc.
def get_state_covid19_data(cd,state,date):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None

    if(not valid_date(cd,date)):
        print("date not valid",date)
        return None

    if(not state in list(state_abbrev.keys())):
        print("invalid state",state)

    covid19_by_county = open('../CSSEGIS-COVID-19/time_series_covid19_' + cd + '_US.csv','r')
    covid19_by_county_reader = csv.reader(covid19_by_county)
    # column headers    
    row = next(covid19_by_county_reader)
    column_headers = row

    date_index = 0
    date_split = [int(d) for d in date.split("/")]
    for x in range(12,len(column_headers)):
        col_date = [int(c) for c in column_headers[x].split("/")]
        if(col_date == date_split):
            date_index = x
            break

    covid19_data = {}
    try:
        while row:
            if(state == row[6]):
                key_name = (str(row[5])+" "+str(state_abbrev[state])).lower()
                covid19_data[key_name] = int(row[date_index])
            row = next(covid19_by_county_reader)
    except StopIteration:
        covid19_by_county.close()
        return covid19_data

    covid19_by_county.close()
    return covid19_data

# state must be full name ex: "New Jersey" NOT "NJ"
# date must be no earlier than 1/22/20 and no later than 6/23/20 (or the most recent date w data)
# returns death count in state on date
# {"County State" : county covid-deaths}, ex. {"Atlantic NJ", ###}, returns None if parameters are invalid
# NOTE: sometimes the total deaths from this function are different than total deaths in get_covid19_by_district because there are rows with deaths not based in a county, some for a city etc.
def get_total_state_covid19_data(cd,state,date):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None

    if(not valid_date(cd,date)):
        print("date not valid",date)
        return None

    if(not state in list(state_abbrev.keys())):
        print("invalid state",state)

    covid19_by_county = open('../CSSEGIS-COVID-19/time_series_covid19_' + cd + '_US.csv','r')
    covid19_by_county_reader = csv.reader(covid19_by_county)
    # column headers    
    row = next(covid19_by_county_reader)
    column_headers = row

    date_index = 0
    date_split = [int(d) for d in date.split("/")]
    for x in range(12,len(column_headers)):
        col_date = [int(c) for c in column_headers[x].split("/")]
        if(col_date == date_split):
            date_index = x
            break

    deaths = 0
    try:
        while row:
            if(state == row[6]):
                key_name = (str(row[5])+" "+str(state_abbrev[state])).lower()
                deaths += int(row[date_index])
            row = next(covid19_by_county_reader)
    except StopIteration:
        covid19_by_county.close()
        return deaths

    covid19_by_county.close()
    return deaths

# county_info is 2D array, each row: [county name,state,county covid-deaths]
# state must be full name, not abbrev ex. "New Jersey", not "NJ"
# date must be no earlier than 1/22/20 and no later than the most recent day on time.....csv (MM/DD/YY)
# returns dictionary containing congressional districts and their death counts
# death count by district is based on proportion of county's population in district on a certain day
def get_covid19_by_district(cd,state,date):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None

    if(not valid_date(cd,date)):
        return None

    if(not state in list(state_abbrev.keys())):
        print("invalid state",state)

    global not_counties
    districts = {}
    district_data = open('../states_and_districts/'+ state_abbrev[state] +'-county-to-district.csv','r')

    district_reader = csv.reader(district_data)
    
    # column headers
    # 1: district #, 2: county name (ex: "Atlantic NJ"), 3: pop, 4: afact
    row = next(district_reader)
    row = next(district_reader)
    row = next(district_reader)
    covid19_by_county = get_state_covid19_data(cd,state,date)
    try:
        while row: 
            county_name = row[2].lower()

            # for Alaska and Louisiana, remove Parish, Borough and Census Area from name
            tokens = word_tokenize(county_name)
            filtered = [w for w in tokens if not (w == 'parish' or w == 'borough' or w == 'census' or w == 'area')]
            county_name = ""
            for w in filtered:
                county_name += (w + " ")
            county_name = county_name[0:len(county_name)-1]

            cong_district = int(row[1])
            afact = float(row[4])
            try:
                if(cong_district == 0):
                    cong_district = 1
                if(cong_district in districts):
                    districts[cong_district] += round(covid19_by_county[county_name]*afact)
                else:
                    districts[cong_district] = round(covid19_by_county[county_name]*afact)
            except KeyError:
                pass
            row = next(district_reader)
    except StopIteration:
        district_data.close()
        return districts
    district_data.close()
    return districts

def get_covid19_by_district_over_time(cd,state,start_date,end_date):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None

    if(not valid_date(cd,start_date)):
        print("invalid start date:",start_date)
        return None
    if(not valid_date(cd,end_date)):
        print("invalid end date:",end_date)
        return None

    if(not state in list(state_abbrev.keys())):
        print("invalid state",state)

    start_date_covid19_counts = get_covid19_by_district(cd,state,start_date)
    district_count = len(start_date_covid19_counts)
    covid19_counts = {}
    for x in range(1,district_count+1):
        covid19_counts[x] = [start_date_covid19_counts[x]]

    date_list = dates_between(cd,start_date,end_date)[1:] # already took care of start_date in creating covid19_counts
    for date in date_list:
        deaths = {k : v for k, v in sorted(get_covid19_by_district(cd,state,date).items())}
        for k,v in deaths.items():
            covid19_counts[k] += [v]

    return covid19_counts

def get_all_covid19_by_state_over_time(cd,start_date,end_date):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None

    if(not valid_date(cd,start_date)):
        print("invalid start date:",start_date)
        return None
    if(not valid_date(cd,end_date)):
        print("invalid end date:",end_date)
        return None

    print("Creating csv of " + cd + "s by state between",start_date,"and",end_date+"...")
    file = open('../' + cd + '_by_district/' + cd + '_by_state_'+start_date.replace("/","_")+"_to_"+end_date.replace("/","_")+".csv","w",newline="")

    writer = csv.writer(file)
    dates = dates_between(cd,start_date,end_date)
    writer.writerow(['state']+dates)

    states = list(state_abbrev.keys())

    for state in states:
        print(state)
        state_deaths = []
        row = [state]
        for date in dates:
            covid19_dict = get_state_covid19_data(cd,state,date)
            covid19_sum = sum(list(covid19_dict.values()))
            row += [covid19_sum]
        
        writer.writerow(row)

# ALL STATES
def get_all_covid19_by_district_over_time(cd,start_date,end_date):
    if(not (cd.lower() == 'deaths' or cd.lower() == 'confirmed')):
        print("cd must be \'deaths\' or \'confirmed\': invalid",cd)
        return None
    if(not valid_date(cd,start_date)):
        print("invalid start date:",start_date)
        return None
    if(not valid_date(cd,end_date)):
        print("invalid end date:",end_date)
        return None

    print("Creating csv of " + cd + " by Congressional District between",start_date,"and",end_date,"...")
    file = open('../' + cd + '_by_district/' + cd + '_by_district_'+start_date.replace("/","_")+'_to_'+end_date.replace("/","_")+'.csv','w',newline='')

    writer = csv.writer(file)
    writer.writerow(['state','district']+dates_between(cd,start_date,end_date))

    states = list(state_abbrev.keys())

    for state in states:
        print(state)
        covid19_counts = get_covid19_by_district_over_time(cd,state,start_date,end_date)
        districts = len(covid19_counts)
        for d in range(1,districts+1):
            writer.writerow([state,d]+covid19_counts[d])
    
    file.close()

if __name__ == '__main__':
    cd = 'deaths'
    update_data(cd)
    
    print("covid19 " + cd + "s over time by Congressional District")
    #start_date = input("Enter a start date (MM/DD/YY): ")
    #end_date = input("Enter an end date (MM/DD/YY): ")

    # NOTE: add input checks

    get_all_covid19_by_district_over_time(cd,"1/22/20","8/3/20")

    '''
    #print(get_covid19_by_district_over_time(cd,"Louisiana","4/20/20","4/26/20"))

    #print(get_state_covid19_data(cd,"Alaska","4/20/20"))
    
    covid19_by_district = open('../../covid19_by_district/covid19_by_district.csv','w',newline='\n')

    district_writer = csv.writer(covid19_by_district)
    district_writer.writerow(['state','district','deaths'])
    states = list(state_abbrev.keys())
    
    for state in states:
        # key = district : value = death count
        state_covid19_by_district = {k : v for k, v in sorted(get_covid19_by_district(cd,state,"6/23/20").items())}
        total = 0
        for k,v in state_covid19_by_district.items():
            district_writer.writerow([state,k,v])
            total += v
        print(state,":",total)

    #print(list(not_counties.keys()))
    '''

    '''
    nj_covid19_by_district = (get_covid19_by_district(cd,"New Jersey"))
    
    nj_covid19_by_district = {k : v for k,v in sorted(nj_covid19_by_district.items())}
    print(nj_covid19_by_district) 
    total1 = 0
    for k,v in nj_covid19_by_district.items():
        total1+=v

    nj_state = get_state_covid19_data(cd,"New Jersey")
    total2 = 0
    for k,v in nj_state.items():
        total2+=v 

    print(total1,total2) 
    # they're off bc of bergen, essex, passaic, and union counties

    ms_covid19_by_district = (get_covid19_by_district(cd,"Missouri"))
    
    ms_covid19_by_district = {k : v for k,v in sorted(ms_covid19_by_district.items())}
    print(ms_covid19_by_district)
    total1 = 0
    for k,v in ms_covid19_by_district.items():
        total1+=v

    ms_state = get_state_covid19_data(cd,"Missouri")
    total2 = 0
    for k,v in ms_state.items():
        total2+=v 

    print(total1,total2) 
    # off bc of Kansas City, 31 deaths in city alone
    # the city falls in many counties?? and 4,5,6 cong. district
    '''
    #deaths_by_district.close()