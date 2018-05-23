import pandas as pd
log=pd.read_csv('P00_2015-02-21_22-07-00.log',sep="\n", header=None)
log.columns=['text']
log.text.apply(str)
for row in log['text']:
    #do logic on each line from the file to search for and save the lines that have the text we want
    if row==row: #check to see if the value is NOT a NaN (i.e.,skip blank lines)
        if "note_on" in row:
            print(row)
            #now select the appropriate values and store them somewhere
