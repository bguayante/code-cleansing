"""
This script matches voter ids from records published 
by the Ohio Secretary of State to a dataset containing a 
secondary subset of voters. It ingests the SOS data from
files created by the get_voter_data.py script and a 
csv containing target voters. The script outputs a csv
containing the dataset of target voters with a new
column containing a matching voterid, if found.
"""

import glob
import pandas as pd
import numpy as np
import re
import csv


class MatchVoterIds():
    
    def __init__(self, input_csv, sos_data_dir):
        self.self = self
        self.input_csv = input_csv
        self.sos_data_dir = sos_data_dir
        self.self.input_df = pd.DataFrame()
        self.sos_df = pd.DataFrame()
        
        
    def create_dataframes(self):
        
        # import target voter dataset
        self.input_df = pd.read_csv(self.input_csv, dtype=str)
        self.input_df.fillna('', inplace=True)
        self.input_df["matched_voterid"] = ''

        # aggregate sos files and combine in dataframe
        sos_files = glob.glob(self.sos_data_dir + "/*.txt")

        frames = []

        for file in sos_files:
            df = pd.read_csv(file, dtype=str)
            frames.append(df)

        agg_sos_records_df = pd.concat(frames, ignore_index=True)

        # keep only sos data fields useful for id matching
        self.sos_df = agg_sos_records_df[['SOS_VOTERID', 'LAST_NAME', 'FIRST_NAME', 'DATE_OF_BIRTH', 
                                    'RESIDENTIAL_ADDRESS1', 'RESIDENTIAL_CITY', 'RESIDENTIAL_ZIP', 
                                    'RESIDENTIAL_STATE']]
        

    def standardize_data(self):
        
        self.self.sos_df.fillna('', inplace=True)
        
        # concatenate FIRST_NAME and LAST_NAME fields to match input_csv fields
        self.sos_df['name'] = self.sos_df.apply(lambda x : x['FIRST_NAME'] + ' ' + x['LAST_NAME'], axis=1)
        
        # extract year from full birth date
        self.sos_df['birth_year'] = (pd.to_datetime(self.sos_df['DATE_OF_BIRTH']).dt.year).astype(int)
        
        self.sos_df['row'] = ''

        # standardize column names to match input dataset
        rename_cols = {
            "RESIDENTIAL_ZIP": "zip",
            "RESIDENTIAL_ADDRESS1": "address",
            "RESIDENTIAL_CITY": "city",
            "RESIDENTIAL_STATE": "state",
            "SOS_VOTERID": "sos_voterid"
        }

        self.sos_df.rename(columns=rename_cols, inplace=True)

        # mask all columns except those present in input_df
        self.sos_df = self.sos_df[["row", "name", "birth_year", "address", "city", "state", "zip", "sos_voterid"]]
     
    
    def merge_and_match(self):
        
        # combine input and sos dataframes 
        merged_df = pd.concat([self.input_df, self.sos_df], ignore_index=True)
        
        # remove unreasonable values for year_of_birth
        # faster to cast value to int than datetime object, get same result
        merged_df["birth_year"].replace({'':0}, inplace=True)
        merged_df["birth_year"] = merged_df["birth_year"].astype(int)

        # transform all strings to upper to standardize casing
        string_cols = ["name", "address", "city", "state"]
        for col in string_cols:
            merged_df[col] = merged_df[col].str.upper()

        # remove middle initials where present
        
        merged_df["name"] = merged_df["name"].apply(lambda x : re.sub(r'\s.\s', ' ', x))
        
        # standardize abbrev for common address suffixes
        replace_add = {
            "STREET": "ST",
            "AVENUE": "AVE",
            "AV": "AVE",
            "DRIVE": "DR",
            "ROAD": "RD",
            "CIRCLE": "CR",
            "STATE ROUTE": "ST RT"
        }

        # From https://stackoverflow.com/a/51537735
        pat = {r'\b{}\b'.format(k):v for k, v in replace_add.items()}
        merged_df["address"].replace(to_replace=pat, regex=True, inplace=True)

        # remove middle initials where present
        merged_df["name"] = merged_df["name"].apply(lambda x : re.sub(r'\s.\s', ' ', x))
        
        # create df of records where "name" and "birth_year" are matches
        
        match_df = pd.DataFrame(columns=merged_df.columns)
        
        # get duplicate records. All input_df rows should be present in new df
        match_df = merged_df[merged_df.duplicated(subset=["birth_year","name"], keep=False) == True]
        match_df = match_df.fillna('')

        for index, x in match_df.iterrows():
            # if the row has a value for "row", it matches a row in self.input_df
            if x["row"]:
                # get its matching row (should be 1 max), add it and match to temp_df
                temp_df = match_df[(match_df["name"] == x["name"]) & (match_df["birth_year"] == x["birth_year"])].fillna('')
                # merge rows (one has value in "row", the other has value in "sos_voterid")
                temp_df = temp_df.max(numeric_only=False).to_frame().transpose()
                # copy values in "row" and "sos_voterid" columns
                row = temp_df["row"][0]
                v_id = temp_df["sos_voterid"][0]
                # find record in self.input_df with matching value in "row"
                idx = self.input_df.index[self.input_df["row"] == row]
                # assign value of temp_df["sos_voterid"] to self.input_df["matched_voterid"]
                self.input_df["matched_voterid"].iloc[idx] = v_id
                
    
    def export_matched_csv(self):
        
        self.input_df.to_csv("data/output/oh_matched_voterids.csv", index=False)
        print("matched voterids saved to data/output/oh_matched_voterids.csv")
        
if __name__ == "__main__":
    input_csv = 'data/input/eng-matching-input-v3.csv'
    sos_data_dir = 'data/input'
    
    mv = MatchVoterIds(input_csv,sos_data_dir)
    mv.create_dataframes()
    mv.standardize_data()
    mv.merge_and_match()
    mv.export_matched_csv()