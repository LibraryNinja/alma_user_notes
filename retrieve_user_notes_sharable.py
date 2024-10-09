import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

#Set up default things for base URL and bib API key
alma_base = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1'

#Set default header for XML
headers = {"Accept": "application/xml"}

#Users/Fulfillment API key:
userapi = 'ENTER-API-KEY-HERE'

#Define empty dictionary for later
dict = {}
dict['userpid'] = []
dict['user_full_name'] = []
dict['user_group'] = []
dict['userexpiry'] = []
dict['note_type'] = []
dict['note_text'] = []
dict['note_hidden_nonprint'] = []
dict['note_user_viewable'] = []
dict['note_popup_status'] = []
dict['note_author'] = []
dict['note_creation_date'] = []

#Bring in input file of user IDs to check for notes
inputname = input("Data Input Filename without extension (must be .xlsx): ")
source = pd.read_excel(inputname + '.xlsx')
userpids=source['userpids'].astype(str)

#Asks user for output filename to use at end of script
outputname = input("Enter filename for output file (without extension): ")

#Main loop, checks user IDs from input file by retreiving user data and extracting specified fields
for j, userpid in enumerate(userpids, 0):
    #Tells user which one we're currently on in the console:
    print(f"Checking record # {str(j+1)} of {str(len(userpids))}")
    userpid = userpids[j]

    #Makes the API Request
    r = requests.get(f"{alma_base}/users/{userpid}?vuser_id_type=all_unique&view=full&expand=none&apikey={userapi}", headers=headers)

    #Turns user data to soup for parsing
    soup = BeautifulSoup(r.content, "xml") 
    
    #Gets user's full name
    try:
        user_name = soup.full_name.string.title()
    except AttributeError:
        user_name = ""
    
    #Gets user's user group
    try:
        usergroup = soup.user_group['desc']
    except TypeError:
        usergroup = ""
        
    #Gets user's expiration date
    try:
        user_expiry = soup.expiry_date.getText()
    except AttributeError:
        user_expiry = ""
    
    #Looks for user notes section
    fullnotes = soup.find_all('user_note')

    #Loops through all notes on user's record
    for i, current_note in enumerate(fullnotes, 0):
        current_note = fullnotes[i]
        
        #Appends user data to each note's entry as it loops
        dict['userpid'].append(userpid)
        dict['user_full_name'].append(user_name)
        dict['user_group'].append(usergroup)
        dict['userexpiry'].append(user_expiry)

        #Gets note type for current note
        try:
            note_type = current_note.note_type['desc']        
        except AttributeError:
            note_type = ""
        dict['note_type'].append(note_type)

        #Gets text for current note and runs a regex check to look for line breaks, adds text and line break check results to dictionary entry
        try:
            note_text = current_note.note_text.getText()
            nonprintmatch = re.search(r'(\\n)+|(\n)+', note_text)
            if nonprintmatch is not None:
                nonprint = True
            else:
                nonprint = False 
        except AttributeError:
            note_text = ""
            nonprint = ""
        dict['note_text'].append(note_text)
        dict['note_hidden_nonprint'].append(nonprint)

        #Checks for "user viewable" flag
        try:
            note_user_view = current_note.user_viewable.getText()
        except AttributeError:
            note_user_view = ""
        dict['note_user_viewable'].append(note_user_view)

        #Checks for "popup note" flag
        try:
            note_popup = current_note.popup_note.getText()
        except AttributeError:
            note_popup = ""
        dict['note_popup_status'].append(note_popup)

        #Checks for note author
        try:
            note_author = current_note.created_by.getText()
        except AttributeError:
            note_author = ""
        dict['note_author'].append(note_author)

        #Checks for note created date (will be blank if empty)
        try:
            note_creation_date = current_note.created_date.getText()
        except AttributeError:
            note_creation_date = ""
        dict['note_creation_date'].append(note_creation_date)

#Converts dictionary to dataframe
df = pd.DataFrame(dict)

#Saves dataframe as Excel file
df.to_excel(outputname + ".xlsx", index=False)