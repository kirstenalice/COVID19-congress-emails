import csv
import re 
from nltk.tokenize import word_tokenize 

stopwords = ["Congress","Governor","Leader","Minority","Majority","Whip","Rep","Rep.","Representative","Representante","Staff","Office","of","Congressman","Congresswoman","Senator","Sen.","U.S.","U.S","US","Dr.","M.D.","M.D","MD","Ph.D",".",",","The","Press"]

def get_name_congress(_from):
    try:
        # names that only have an email in csv, no name
        if('Fulcher' in _from):
            return 'Russ Fulcher'
        elif('JamesRisch' in _from):
            return 'James Risch'
        elif('Newsletter@rosen' in _from):
            return "Jacky Rosen"
        elif('FL24FW' in _from):
            return "Frederica Wilson"
        elif('VA04DM' in _from):
            return "Donald McEachin"
        name = _from[0:_from.index('<')]
        name = re.sub(r'["]',"",name)
        name = re.sub(r'[:]',"",name)

        tokenized_name = word_tokenize(name)
        filtered_name = [w for w in tokenized_name if not w in stopwords]

        final_name = ""

        for w in filtered_name:
            final_name = final_name + w + " "

        # names that are slightly different in hs116-members.csv vs their From email signatures
        if('Bobby Scott' in final_name):
            return "Robert Scott"
        elif('Jeff Van Drew' in final_name):
            return "Jefferson Van Drew"
        elif('John Carney' in final_name): # Governor, not congress
            return ""
        elif('Tom Reed' in final_name):
            return "Thomas Reed"
        elif('Scott Shop' in final_name):
            return "Tim Scott"
        elif('Don Young' in final_name):
            return 'Donald Young'
        elif('Sam Graves' in final_name):
            return "Samuel Graves"
        elif('McConnell' in final_name):
            return "Mitch McConnell"
        elif('Manchin' in final_name):
            return "Joe Manchin"
        elif('Pingree' in final_name):
            return "Chellie Pingree"
        elif('Dusty Johnson' in final_name):
            return "Dustin Johnson"
        elif('Carper' in final_name):
            return "Tom Carper"
        elif('e-kilili' in final_name):
            return "Gregorio Kilili Camacho Sablan"
        elif('DeGette' in final_name):
            return "Diana DeGette"
        elif('Sinema' in final_name):
            return "Kyrsten Sinema"
        elif('A .Donald McEachin' in final_name):
            return "Donald McEachin"
        elif('Blumenauer Earl' in final_name or 'Daniel Schwarz' in final_name):
            return "Earl Blumenauer"
        elif('Durbin Report' in final_name):
            return "Richard Durbin"
        elif('Titus' in final_name):
            return "Dina Titus"
        elif('Markey' in final_name):
            return "Ed Markey"
        elif('Clyburn' in final_name):
            return "Jim Clyburn"
        elif('Napolitano' in final_name):
            return 'Grace Flores Napolitano'
        elif('Wittman' in final_name):
            return "Rob Wittman"
        elif('Cornyn' in final_name):
            return 'John Cornyn'
        elif('Murphy ' in final_name or 'Greg Murphy' in final_name):
            return 'Gregory Murphy'
        elif('Braun' in final_name):
            return 'Michael Braun'
        elif('desaulnier' in final_name.lower()):
            return 'Mark DeSaulnier'
        elif('Mike Thompson' in final_name):
            return "Michael Thompson"
        elif('Joe Kennedy' in final_name):
            return "Joseph Kennedy"
        elif('Conn Carroll' in final_name):
            return "Mike Lee"
        elif('Susan W. Brooks' in final_name):
            return "Susan Brooks"
        elif('Hyde Smith' in final_name):
            return 'Cindy Hyde-Smith'

        return final_name[0:len(final_name)-1]
    except ValueError:
        return _from


if __name__ == "__main__":
    reader = csv.reader(open('../covid_thru_8_20_20.csv',newline=''))

    writer = csv.writer(open('../covid19-aug-names.csv',"w",newline='\n'))

    # append new row that contains full name of congressperson
    
    colnames = next(reader)[0:4]
    colnames = colnames + ['Name!!!!']

    writer.writerow(colnames)
    row = next(reader)
    
    get_name_congress(row[1])
    try:
        while row:
            # if row is empty, skip the row
            if(not re.search('[a-zA-Z]', row[1])):
                writer.writerow(row)
                row = next(reader)
                continue
            filtered_name = get_name_congress(row[1])
            print(filtered_name)

            writer.writerow(row[0:4]+[filtered_name])
            row = next(reader)
    except StopIteration:
        print('done')
    