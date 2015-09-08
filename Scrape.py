import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import datetime
import time



# Scrape function with 4 arguments: the phone model or brand (String), the number of
# pages that will have to scraped (Int), the list of locations you want data about,
# the day (format: 'YYYY-MM-DD'), and the name of the csv output file (String.csv).
def scrape(phoneModel, pages, locations, date, outputFile):

    items = []

    for location in locations:
        websiteUrl = "http://" + str(location) + ".craigslist.org"
        baseUrl = "http://" + str(location) + ".craigslist.org/search/moa?minAsk=60"

        modelUrl = baseUrl + '&query=' + str(phoneModel)

        for i in range(0, pages):

            if i > 0:
                url = modelUrl + "&s=" + str(100*i)
            else:
                url = modelUrl

            try:
                r = requests.get(url)
            except:
                continue
            soup = BeautifulSoup(r.content)
            ads = soup.find_all('p', {"class": "row"})


            for ad in ads:

                # extract ad ID
                PID = ad.get("data-pid")
                # extract ad title
                title = ad.find('a', {"class": "hdrlnk"}).text
                TITLE = title.encode('utf-8')
                # extract ad price
                PRICE = ad.a.find('span', {"class": "price"}).text
                # extract ad location
                LOCATION = str(location)
                # extract ad current date
                UPDATE_DATE = ad.time.get("datetime")

                # extract specific info from ad's link
                link = ad.a.get("href")
                LINK = websiteUrl + str(link)
                try:
                    r_ad = requests.get(LINK)
                except:
                    continue
                soup_ad = BeautifulSoup(r_ad.content)
                try:
                    POSTED_DATE = soup_ad.find('p', {"class": "postinginfo"}).time.text
                except:
                    POSTED_DATE = 'NaN'
                if date in POSTED_DATE:
                    print POSTED_DATE
                    item = [PID, LINK, TITLE, PRICE, LOCATION, UPDATE_DATE, POSTED_DATE, 'Not Sold Yet']
                    items.append(item)
                else:
                    continue


    with open(outputFile, "wb") as f:
        writer = csv.DictWriter(f, fieldnames = ["PID", "LINK", "TITLE", "PRICE", "LOCATION", "UPDATE_DATE", "POSTED_DATE", "SOLD_BY"])
        writer.writeheader()
        writer = csv.writer(f)
        writer.writerows(items)
        print str(phoneModel) + 'data has been scraped.'




# Check if every url in the input csv file still contains an ad. If a url does
# not, then its associated value in the SOLD_BY column is changed to the current
# date, and this value won't be modified again.
def checkSale(csvFileInput, csvFileOutput):
    soldby = []
    df = pd.read_csv(csvFileInput)
    for (url, sale) in zip(df.LINK, df.SOLD_BY):
        if sale == 'Not Sold Yet':
            try:
                r = requests.get(url)
            except:
                sale = 'Ad Gone.'
            ad = BeautifulSoup(r.content)
            try:
                removed = ad.find('div', {'class':'removed'})
                if removed:
                    sale = str(datetime.datetime.now())
            except:
                continue
            print url, sale
        soldby.append(sale)
    df.SOLD_BY = soldby
    df.to_csv(csvFileOutput)

filename = 'dataiPhone_' + time.strftime("%d-%m-%Y")
scrape('iphone', 10, ['sfbay', 'chicago', 'newyork', 'losangeles', 'houston'], filename)
#checkSale(<old>,filename)
