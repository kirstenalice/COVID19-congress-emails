import csv
import re 
import nltk
from nltk.tokenize import word_tokenize

import json

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
# county must be full name
# state must be full name, not abbrev ex. "New Jersey", not "NJ"
# returns number of deaths in a county
def get_county_death_data(county,state):
    # reader for the csv file
    deaths_by_county = open('CSSEGIS-COVID-19/time_series_covid19_deaths_US.csv','r')
    deaths_by_county_reader = csv.reader(deaths_by_county)
    # column headers    
    row = next(deaths_by_county_reader)
    try:
        while row and not (row[5] == county and row[6] == state):
            row = next(deaths_by_county_reader)
    except StopIteration:
        print("death data not found for",county,'county',state)
        return None
    print('Deaths in',county,'county,',state,':',row[len(row)-1])
    deaths_by_county_reader.close()
    return row[len(row)-1]

# returns dictionary of state's covid19 death data by county
# {"County State" : county covid-deaths}, ex. {"Atlantic NJ", ###}
# NOTE: sometimes the total deaths from this function are different than total deaths in get_death_by_district because there are rows with deaths not based in a county, some for a city etc.
def get_state_death_data(state):
    deaths_by_county = open('CSSEGIS-COVID-19/time_series_covid19_deaths_US.csv','r')
    deaths_by_county_reader = csv.reader(deaths_by_county)
    # column headers    
    row = next(deaths_by_county_reader)
    deaths_data = {}
    try:
        while row:
            if(state == row[6]):
                key_name = (str(row[5])+" "+str(state_abbrev[state])).lower()
                deaths_data[key_name] = int(row[len(row)-1])
            row = next(deaths_by_county_reader)
    except StopIteration:
        deaths_by_county.close()
        return deaths_data

    deaths_by_county.close()
    return deaths_data

# county_info is 2D array, each row: [county name,state,county covid-deaths]
# state must be full name, not abbrev ex. "New Jersey", not "NJ"
# returns dictionary containing congressional districts and their death counts
# death count by district is based on proportion of county's population in district
def get_death_by_district(state):
    global not_counties
    districts = {}
    district_data = open('states_and_districts/'+ state_abbrev[state] +'-county-to-district.csv','r')

    district_reader = csv.reader(district_data)
    
    # column headers
    # 1: district #, 2: county name (ex: "Atlantic NJ"), 3: pop, 4: afact
    row = next(district_reader)
    row = next(district_reader)
    row = next(district_reader)
    deaths_by_county = get_state_death_data(state)
    try:
        while row: 
            county_name = row[2].lower()
            cong_district = int(row[1])
            county_pop = int(row[3])
            afact = float(row[4])
            try:
                if(cong_district in districts):
                    #if(not afact == 1.0):
                    #   print(county_name+" "+str(cong_district)+" "+str(deaths_by_county[county_name])+" * "+str(afact)+" = "+str(deaths_by_county[county_name]*afact)+" "+str(round(deaths_by_county[county_name]*afact)))
                    districts[cong_district] += round(deaths_by_county[county_name]*afact)
                else:
                    #if(not afact == 1.0):
                #     print(county_name+" "+str(cong_district)+" "+str(deaths_by_county[county_name])+" * "+str(afact)+" = "+str(deaths_by_county[county_name]*afact)+" "+str(round(deaths_by_county[county_name]*afact)))
                    districts[cong_district] = round(deaths_by_county[county_name]*afact)
            except KeyError:
                not_counties[county_name] = 1
            row = next(district_reader)
    except StopIteration:
        return districts
    return districts

if __name__ == '__main__':
    deaths_by_district = open('deaths_by_district/deaths_by_district.csv','w',newline='\n')

    district_writer = csv.writer(deaths_by_district)
    district_writer.writerow(['state','district','deaths'])
    states = list(state_abbrev.keys())
    
    for state in states:
        state_deaths_by_district = {k : v for k, v in sorted(get_death_by_district(state).items())}
        total = 0
        for k,v in state_deaths_by_district.items():
            district_writer.writerow([state,k,v])
            total += v
        print(state,":",total)

    print(list(not_counties.keys()))
    
    '''
    nj_deaths_by_district = (get_death_by_district("New Jersey"))
    
    nj_deaths_by_district = {k : v for k,v in sorted(nj_deaths_by_district.items())}
    print(nj_deaths_by_district) 
    total1 = 0
    for k,v in nj_deaths_by_district.items():
        total1+=v

    nj_state = get_state_death_data("New Jersey")
    total2 = 0
    for k,v in nj_state.items():
        total2+=v 

    print(total1,total2) 
    # they're off bc of bergen, essex, passaic, and union counties

    ms_deaths_by_district = (get_death_by_district("Missouri"))
    
    ms_deaths_by_district = {k : v for k,v in sorted(ms_deaths_by_district.items())}
    print(ms_deaths_by_district)
    total1 = 0
    for k,v in ms_deaths_by_district.items():
        total1+=v

    ms_state = get_state_death_data("Missouri")
    total2 = 0
    for k,v in ms_state.items():
        total2+=v 

    print(total1,total2) 
    # off bc of Kansas City, 31 deaths in city alone
    # the city falls in many counties?? and 4,5,6 cong. district
    '''
