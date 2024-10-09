# Alma User Notes
Scripts to work with user notes in Alma

This repository has two scripts for working with Alma user notes. 

# Retrieve User Notes
Takes an input file of Primary Identifiers and pulls all associated notes for them, outputting to an Excel spreadsheet. Includes fields not available in Analytics including note creator, note creation date, and "popup note" flag. It also checks to see if the text of the note includes /n line breaks (because they don't play nice with the subsequent script). 

- Requires Users/Fulfillment API Key (Read-only or Read/Write)

# Edit User Notes
Takes input file of Primary Identifiers and full note text. Loops through deduped list of Primary Identifiers, retrieves user data, and hunts for notes with matching text to remove. Removes the parent and siblings of the specified note(s) before sending the data back to Alma.

Currently has a hard time with notes containing /n line breaks. (They turn kind of invisible when retrieved and it's hard to match them to remove them.)

- Requires Users/Fulfillment API Key (Read/Write)
