import csv
import re 
from nltk.tokenize import word_tokenize 

stopwords = ["Congress","Governor","Leader","Minority","Majority","Whip","Rep","Rep.","Representative","Representante","Staff","Office","of","Congressman","Congresswoman","Congresman","Senator","Sen.","U.S.","U.S","US","Dr.","M.D.","M.D","MD","Ph.D",".",",","The","Press"]

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
        elif('MN07' in _from):
            return "Collin Peterson"
        elif('sessions.newsletter' in _from):
            return 'Jeff Sessions'
        elif('cassidy.enews' in _from):
            return "Bill Cassidy"
        elif('MD06JDIMA' in _from):
            return "John Delaney"
        elif('representative.reichert' in _from):
            return 'Dave Reichert'
        elif('Heitkamp' in _from):
            return "Heidi Heitkamp"
        elif('Valadao' in _from):
            return "David Valadao"
        elif('Congresswoman Cheney' in _from):
            return "Liz Cheney"

        name = _from[0:_from.index('<')]
        name = re.sub(r'["]',"",name)
        name = re.sub(r'[:]',"",name)

        tokenized_name = word_tokenize(name)
        filtered_name = [w for w in tokenized_name if not w in stopwords]

        final_name = ""

        for w in filtered_name:
            final_name = final_name + w + " "

        # names that are slightly different in hs116-members.csv vs their From email signatures
        if(final_name == 'Bobby Scott '):
            return "Robert Scott"
        elif(final_name == 'Jeff Van Drew '):
            return "Jefferson Van Drew"
        elif(final_name == 'John Carney '): # Governor, not congress
            return ""
        elif(final_name == 'Tom Reed '):
            return "Thomas Reed"
        elif(final_name == 'Scott Shop '):
            return "Tim Scott"
        elif(final_name == 'Don Young '):
            return 'Donald Young'
        elif(final_name == 'Sam Graves '):
            return "Samuel Graves"
        elif(final_name == 'McConnell '):
            return "Mitch McConnell"
        elif(final_name == 'Manchin '):
            return "Joe Manchin"
        elif(final_name == 'Pingree '):
            return "Chellie Pingree"
        elif(final_name == 'Dusty Johnson '):
            return "Dustin Johnson"
        elif(final_name == 'Carper '):
            return "Tom Carper"
        elif('e-kilili' in final_name):
            return "Gregorio Kilili Camacho Sablan"
        elif(final_name == 'DeGette '):
            return "Diana DeGette"
        elif(final_name == 'Sinema '):
            return "Kyrsten Sinema"
        elif(final_name == 'A .Donald McEachin '):
            return "Donald McEachin"
        elif(final_name == 'Blumenauer Earl ' or 'Daniel Schwarz' in final_name):
            return "Earl Blumenauer"
        elif(final_name == 'Durbin Report '):
            return "Richard Durbin"
        elif(final_name == 'Titus '):
            return "Dina Titus"
        elif(final_name == 'Markey '):
            return "Ed Markey"
        elif(final_name == 'Clyburn '):
            return "Jim Clyburn"
        elif(final_name == 'Napolitano '):
            return 'Grace Flores Napolitano'
        elif(final_name == 'Wittman '):
            return "Rob Wittman"
        elif(final_name == 'Cornyn '):
            return 'John Cornyn'
        elif(final_name == 'Murphy ' or 'Greg Murphy' in final_name):
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
        elif('Fortenberry' in final_name):
            return 'Jeff Fortenberry'

        return final_name[0:len(final_name)-1]
    except ValueError:
        return _from


if __name__ == "__main__":
    reader = csv.reader(open('./laina/immigration.csv',newline=''))

    writer = csv.writer(open('./laina/immigration-names.csv',"w",newline='\n'))

    # append new row that contains full name of congressperson
    
    colnames = next(reader)[0:4]
    colnames = colnames + ['Name']

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

            writer.writerow(row[0:4]+[filtered_name])
            row = next(reader)
    except StopIteration:
        print('done')
    