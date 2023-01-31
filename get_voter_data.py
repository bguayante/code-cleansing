"""
This script crawls the Ohio Secretary of State's Voter
File Download page and saves to file data from the 
counties associated with each element in {record_nums}.
"""

import cloudscraper

def get_records(url, record_nums):

    # site utilizes Cloudflare's IUAM, cloudscraper will bypass it
    scraper = cloudscraper.create_scraper()

    # iterate through the list of counties in {record_nums} and
    # save text downloaded from each to file
    for num in record_nums:
        num = str(num)
        res = scraper.get(url + num)
        with open(f"data/input/ohio_vrecords_county_{num}.txt", 'w') as f:
            f.write(res.text)
    
    print("voter data downloaded to data/input")


if __name__ == "__main__":

    # base URL to which county numbers will be appended
    url = "https://www6.ohiosos.gov/ords/f?p=VOTERFTP:DOWNLOAD::FILE:NO:2:P2_PRODUCT_NUMBER:"

    # nums corresponding to county numbers
    record_nums = range(1,5)

    get_records(url, record_nums)