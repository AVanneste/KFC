import requests
import datetime
from os.path import exists
import pandas as pd
import datetime

def getFeed():
    
    #using requests to get the xml file that's updated every minute on the flemish official website
    #there's an issue with the ssl certificate so we choose to ignore the warning
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    url = 'https://miv.opendata.belfla.be/miv/verkeersdata'

    #using try/except in case the site is down
    #if we get the xml, the file is overwritten every time, no need to keep it
    try:
    
        response = requests.get(url, verify=False)

        with open('feed.xml', 'wb') as file:
            file.write(response.content)
            print("new feed file saved at : ", datetime.datetime.now())
    
    #it there's an issue and the file can't get updated, it's logged in a csv file
    except:
        
        file_exists = exists('no_updates.csv')
        columns = ['no_update_time']
        
        if file_exists:
            
            df_err = pd.read_csv('no_update.csv')
            
        else:
            
            df_err = pd.DataFrame(columns=columns)
        
        df_err.loc[len(df_err)] = datetime.datetime.now()
        df_err.to_csv('no_update.csv')
        print('couldnt get updated feed, logged in error file')