# Matching Ohio State VoterIDs 

This repo contains scripts to be used to download voter information from the Ohio Secretary of State's website and match the voters it contains to a list of targetted voters to retrieve their VoterIDs. 

`get_voter_data.py` contains code to fetch the voter files from the Ohio SOS's site and save it to disk.  
`match_voterid.py` contains code to match the voter information in both files and save a new dataset containing the targetted voters and their SOS-issued VoterIDs to disk when matches are possible.

## Requirements

- python >= 3.11
- pipenv >= 2022.10.11

## Setting Up the Environment

Create a virtual environment with `pipenv` and install dependencies by executing the following commands in a terminal or command prompt window.
   
```sh
pipenv sync
pipenv shell
```

## Approach

Data fields present in the targetted voter list and the SOS data were surveyed to determine which could be mapped and which could be ignored. It was largely possible to directly map and filter the SOS dataset to the targetted voter field names to create standardized sets.

The `name` and `birth_year` fields were considered to be the most reliable datapoints on which to infer a match between voter records. `address` was also considered to be reliable for this exercise, though in practice it is usually difficult to verify across (or even within) datasets due to the variation introduced by differing collection techniques and the fact that the value can change over time. 

`sos_voterid` was used as a final confirmation when differentiating between voters with identical names, birth years, and even addresses. The possibility that these were issued in error so that a single voter could be associated with multiple IDs would be a real concern with real data, but was treated as accurate in the absence of ways to verify it. 

For comparison purposes, the casing of values in the `name` field was standardized and middle initials were removed where present. While middle name can be used to distinguish between individuals, it was not provided consistently enough to use as a measure. It would be possible to test for matches of two possible values for each `name` associated with each voter record, but the differences in total voter matches was negligible when tested.

`address`es were also standardized. Casing was made consistent between the two sets and some of the strongs commonly found in addresses were standardized (i.e., STREET was standarized to ST). Matches were more common with these changes and a review of the datasets at this point did not suggest that many near-matches that could be considered to reflect the same location existed. It would be possible to check this more thoroughly using fuzzy matching techniques, but they are very computationally expensive and did not appear to be worthwhile.

In total, 81 of 300 records in the targetted voters dataset were matched with SOS-issued voterIDs. Considering the size of the SOS dataset, this number seems low, but can be explained by the fact that all data was considered accurate. In reality, this would probably result in a discussion with colleagues better-versed in Ohio election practices so that inferences could be made about missing values or to learn whether a particular datapoint could be treated as more or less reliable.

## Areas for Improvement

If the goal was to extract all voter matches regardless of cost, it would be beneficial to create multiple name fields: one with the names as recorded, one containing first, middle, and last names, and another containing first, middle initials, and last names. Some first names were also provided with initials, but the amount of variation possible in the field makes it difficult to cover all cases where matches could be present but difficult to detect using string comparison.

As mentioned above, address information could be more accurately matched using a library like `fuzzywuzzy` to attempt to match similar values, but from experience using it with short strings in a large dataset, it is extremely slow to produce results.

Finally, though they were included in the datasets, `city` and `zip` information was not considered in comparisons though it's possible that the same address may exist in different cities. Given the size of the datasets, it probably wouldn't have been worthwhile to verify, but it would be useful in larger sets or if near-perfect accuracy was required.

## Note
It was not mentioned in the instructions, but the Ohio Secretary of State's website is protected by Cloudflare, which prevents programmatic scraping of websites for data. The library `cloudscraper` was used to bypass this limitation, but as Cloudflare is continually developing its product, `cloudscraper` cannot be relied upon to always be capable of overcoming its restrictions. This is mentioned both to flag it as a potential issue with the exercise and because it is useful technical knowledge to have as it is not immediately obvious why connections to the site fail when executed through a script.