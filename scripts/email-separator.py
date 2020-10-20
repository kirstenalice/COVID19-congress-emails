import csv

if __name__ == '__main__':
    emails_raw = open('../covid_thru_8_20_20.csv','r')

    reader = csv.reader(emails_raw)
    
    row = next(reader)

    x = 0
    while (row and x < 1000):
        if(x == 0): # empty csv
            break
        


        x += 1

        if(x == 1000):
            # close csv and save it