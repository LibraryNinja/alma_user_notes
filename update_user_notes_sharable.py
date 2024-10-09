import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime

date = datetime.now().strftime("%m%d%y")

#Sets up logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, filename="update_user_notes.log", datefmt='%Y-%m-%d %H:%M:%S')

#Update log file
logging.info("Script started-" + date)

#Set up default things for base URL and bib API key
alma_base = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1'

#Sets header to XML and also content-type for data return
headers = {"Accept": "application/xml", "content-type": "application/xml"}

#Users/Fulfillment R/W API key:
userapi = 'ENTER-API-KEY-HERE'

#Import file of notes to remove that includes user IDs and notes to be removed
inputname = input("Data Input Filename without extension (must be .xlsx): ")
df = pd.read_excel(inputname + '.xlsx', dtype='str', keep_default_na=False)

#Create deduplicated list of user IDs (so we can check each user once even if they have multiple notes)
df_userlist = df['userpid']
df_userlist.drop_duplicates(inplace=True)

#Makes that dataframe a list
userpids=df_userlist.tolist()

#Loop through standalone list of user IDs, pull that user's metadata, find the notes from the input file and remove them from the data
for i, userpid in enumerate(userpids, 0):
    #Tells user where in the process we are
    print(f"Checking record # {str(i+1)} of {str(len(userpids))}")
    
    userpid = userpids[i]
    #Logs process
    logging.info(f"Processing {userpid}, entry # {str(i+1)} of {str(len(userpids))}")

    #Pulls user's data
    r = requests.get(f"{alma_base}/users/{userpid}?vuser_id_type=all_unique&view=full&expand=none&apikey={userapi}", headers=headers)

    #Turns user's data to soup for parsing/editing
    soup = BeautifulSoup(r.content, "xml") 
    
    #Find block containing user notes
    blocknotes = soup.find('user_notes')
    #Logs original notes
    logging.info(f"Original notes: {blocknotes}")

    #Find notes to remove for user
    notesforuser = (df.loc[df['userpid'] == userpid, 'note_text'])
    print(f"Number of notes to remove : {len(notesforuser)}")
    
    #Loop through notes to remove and extract them from user data XML
    for k, note in enumerate(notesforuser, 0):        
        notestring = notesforuser.iloc[k]

        noteselect = blocknotes.find('note_text', string = notestring)

        #Make sure that note is even there before trying to remove it
        try:
            #Find parent/siblings for specified note
            noteparent = noteselect.parent

            #Extract/remove the specified note from the XML
            updatenotes = noteparent.extract()
        
        #Skip if no exact match
        except AttributeError:
            pass
            
        
    logging.info(f"Updated notes: {blocknotes}")
    
    #Sends updated data back to Alma
    updatepush = requests.put(f"{alma_base}/users/{userpid}?vuser_id_type=all_unique&view=full&expand=none&apikey={userapi}", data=soup.encode('utf-8'), headers=headers)
    
    #Logs status code and reason returned from PUT request
    logging.info(updatepush.status_code)
    logging.info(updatepush.reason)