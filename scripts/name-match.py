import csv
import re 
from nltk.tokenize import word_tokenize 

repeated_last_names = ["AMASH","BISHOP",'BLUNT','BROOKS','BROWN','CARTER','COLLINS','DAVIS','GARCIA','GONZALEZ','GRAVES','GREEN','HARRIS','HIGGINS','HILL','JOHNSON','JONES','JOYCE','KELLY','KENNEDY','KING','LEE','LEVIN','MALONEY','MURPHY','PETERS','REED','RICE','ROGERS','ROSE','SCOTT','SMITH','THOMPSON','TORRES','VAN','WILSON','YOUNG'] # AMASH and VAN (DREW) are duplicates of the same person in the csv

set_of_unmatched_names = set([])

def find_congress_data(emails_row):
    '''
      - get filtered name from emails csv, pull last name
      - find last name in members csv
      - add this data to the emails csv
    '''

    # bioname = col 9 in data
    
    data = open('./hs116-members.csv',newline='')
    data_reader = csv.reader(data)
    
    # gets column names
    row = next(data_reader)
    # skips to first row of data
    row = next(data_reader)

    # data row that matches the sender of emails_row 
    match = []
    match_name = ""
    while row:
        try:
            email_name = emails_row[4].lower()
            data_name = row[9].lower()

            if('á' in email_name):
                email_name = email_name.replace('á','a')
            if('á' in data_name):
                data_name = data_name.replace('á','a')

            if(len(email_name) == 0):
                print('name empty: ',email_name)
                return []

            email_name_token = word_tokenize(email_name)
            data_name_token = word_tokenize(data_name)

            last_name = email_name_token[len(email_name_token)-1]
            first_name = email_name_token[0]

            if(last_name in data_name_token):
                is_last_name_dupl = last_name.upper() in repeated_last_names
                if(is_last_name_dupl):

                    is_subset = set(email_name_token).issubset(set(data_name_token))

                    if(is_subset):
                        match = row
                        data.close()
                        return match
                else:
                    match = row
                    match_name = row[9]
                    data.close()
                    return match
            
            row = next(data_reader)
        except StopIteration:
            data.close()
            set_of_unmatched_names.add(emails_row[4])
            return match


if __name__ == "__main__":
    print('starting name matching....')
    # file with emails in it
    emails = open('./covid19-dem-names.csv',newline='')
    # file with congresspeople data in it
    data = open('./hs116-members.csv',newline='')

    emails_reader = csv.reader(emails)
    data_reader = csv.reader(data)

    # file to have combined email and congresspeople data
    writer = csv.writer(open('./covid19-dem-emails-and-data.csv',"w",newline='\n'))

    emails_colnames = next(emails_reader)[0:6]
    data_colnames = next(data_reader)[0:21]
    colnames = emails_colnames + data_colnames

    writer.writerow(colnames)

    # make sure to close this file, bc it will be reopened in a new reader in add_congress_data
    data.close()

    emails_row = next(emails_reader)

    count = 0
    try:
        while emails_row and count < 4000:
            # if row is empty, skip the row
            if(not re.search('[a-zA-Z]', emails_row[4])):
                writer.writerow(emails_row)
                emails_row = next(emails_reader)
                continue

            data_row = find_congress_data(emails_row)

            #print(emails_row[0:5] + data_row)
            writer.writerow(emails_row[0:6] + data_row)

            emails_row = next(emails_reader)
            count = count + 1
    except StopIteration:
        print("done")
        print(set_of_unmatched_names)

