from get_feed import getFeed
from get_data import getData
import schedule
import time
import datetime

if __name__ == "__main__":
    
    schedule.every().minute.at(':10').until(datetime.timedelta(weeks=1)).do(getFeed)
    schedule.every().minute.at(':15').until(datetime.timedelta(weeks=1)).do(getData)

    
    while True:
        schedule.run_pending()
        time.sleep(1)
