import pandas as pd
import xml.etree.ElementTree as ET
import datetime
from os.path import exists


def getData():
    #open the xml file (updated each minute) and parse it
    xmldata = 'feed.xml'
    tree = ET.parse(xmldata)
    root = tree.getroot()

    #extract update time
    tijd_publicatie = root.find('tijd_publicatie').text
    date = datetime.datetime.fromisoformat(tijd_publicatie)
    datum = tijd_publicatie[:10]
    day = date.strftime("%A")
    #add 1 so that it's rounded to the Xth hour
    hour = int(date.strftime("%H")) + 1

    #check if csv file already exists then opens or creates it
    file_exists = exists('verkeersdata.csv')
    columns = ['meetpunt_id', 'beschikbaar', 'defect', 'geldig', 'verkeersintensiteit', 'datum', 'dag',
        'u1', 'u2', 'u3', 'u4', 'u5', 'u6', 'u7', 'u8', 'u9', 'u10', 'u11', 'u12', 'u13', 'u14', 'u15', 'u16', 'u17', 'u18', 'u19', 'u20', 'u21', 'u22', 'u23', 'u24',
        'updated', 'not_updated', 'last_updated']
    if file_exists:
        
        df = pd.read_csv('verkeersdata.csv')
        
    else:
        
        df = pd.DataFrame(columns=columns)

    #check if 'last updated' time already in file, in case we didn't get the latest feed.xml
    if not df['last_updated'].isin([str(date)]).any():
        
        #creates a new momentary df that will be appended in the end to the main df if not empty
        df_new = pd.DataFrame(columns=columns)
        
        #iterates through xml file to get all data
        for elem in root.iter('meetpunt'):
            meetpunt_id = elem.attrib.get('unieke_id')
            beschikbaar = elem.find('beschikbaar').text
            defect = elem.find('defect').text
            geldig = elem.find('geldig').text
            
            #summing all the counts from all the vehicles categories
            count = 0
            for meet_elem in elem.iter('meetdata'):
                verkeersintensiteit = meet_elem.find('verkeersintensiteit').text
                count += int(verkeersintensiteit)
            
            #checks if there's already some data for that specific 'meetpunt' and date
            values_list = (df.loc[(df['meetpunt_id']==int(meetpunt_id)) & (df['datum']==str(datum))].values).tolist()
            
            #if yes, we add the latest minute count to the corresponding hour
            if values_list :
                
                previous_count = values_list[0][6+int(hour)]
                new_count = previous_count + count
                df.loc[(df['meetpunt_id'] == int(meetpunt_id)) & (df['datum'] == str(datum)), 'u'+str(hour)] = new_count
                df.loc[(df['meetpunt_id'] == int(meetpunt_id)) & (df['datum'] == str(datum)), 'last_updated'] = date
                df.loc[(df['meetpunt_id'] == int(meetpunt_id)) & (df['datum'] == str(datum)), 'updated'] +=1
            
            #or else, adds a new row with new date (in the momentary df)
            else:
                
                hours_list = [0]*26
                hours_list[hour-1] = count
                data = [meetpunt_id, beschikbaar, defect, geldig, count, datum, day]
                data.extend(hours_list)
                data.append(date)
                df_new.loc[len(df_new)] = data

        #appends the dfs together
        if not df_new.empty:
            df = pd.concat([df,df_new])
            
    #if the 'last updated' time already exists in the df, then we don't update the count but increment the 'not updated' value
    else:
        
        df.loc[df['datum'] == str(datum), 'not_updated'] +=1
            
    #sums the hours count for day total
    df['verkeersintensiteit'] = df[['u1', 'u2', 'u3', 'u4', 'u5', 'u6', 'u7', 'u8', 'u9', 'u10', 'u11', 'u12', 'u13', 'u14', 'u15', 'u16', 'u17', 'u18', 'u19', 'u20', 'u21', 'u22', 'u23', 'u24']].sum(axis=1)

    #overwrites file
    df.to_csv('verkeersdata.csv', index=False)
    print("new verkeersdata file saved at : ", datetime.datetime.now())