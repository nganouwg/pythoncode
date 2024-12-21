'''
    Read a file line by line
'''

import os
import re
import pandas as pd
from typing import List
from dotenv import load_dotenv
import sqlalchemy as sa

load_dotenv()

pattern = r"\d{2}-\d{4}"

def findexp(desc: List[str]):
    try : 
        return desc.index("Illustrative") #starting at 0
    except:
        return -1

with open("/Users/georgesnganou/Documents/Projects/Data/occupations.txt") as file:
    
    occdf = pd.DataFrame(columns=['ID', 'Occ'])
    occtypedf = pd.DataFrame(columns=['ID', 'OccID', "occType"])
    occtypedescdf = pd.DataFrame(columns=['ID', 'OccID', 'Desc'])
    titledf = pd.DataFrame(columns=['OccID', 'Title'])
    
    id = None
    occ = None
    occTypeID = None
    occType = None
    occTypeDescID = None
    occTypeDesc = None
    jobtitles = None

    i = 0
    tb = 0
    
    lines = file.readlines()

    for i in range(100):
        words = lines[i].split()

        #print(words)

        if len(words) > 1:
            if re.fullmatch(pattern, words[0]):   #If the first word is an ID
                id = words[0]
                occ = " ".join(words[1:])
                #print(id, " -- ", occ) 
                occdf.loc[len(occdf)] = [id, occ]        
            elif words[0] == '•':                 #If the first word is a dot "•"
                if len(words) < 15:
                    if re.fullmatch(pattern, words[1]):
                        occTypeID = words[1]
                        occType = " ".join(words[2:])
                        occtypedf.loc[len(occtypedf)] = [occTypeID, id, occType]
                        #print(occTypeID, " -- ", occType)
                else:
                    if re.fullmatch(pattern, words[1]):
                        occTypeDescID = words[1]
                        tb = findexp(words)
                        if tb == -1:
                            occTypeDesc = " ".join(words)
                        else:
                            occTypeDesc = " ".join(words[2:tb])
                            jobtitles = " ".join(words[tb+2:]).split(",")

                        occtypedescdf.loc[len(occtypedescdf)] = [occTypeDescID, id, occTypeDesc]
                        #print(occTypeDescID, " -- ", occTypeDesc)
                        df = pd.DataFrame({"OccID":id, "Title": jobtitles})
                        titledf = pd.concat([titledf, df], ignore_index=True)
                        #print(jobtitles)
                    pass

    print(occdf)
    print(occtypedf)
    print(occtypedescdf)
    print(titledf)

    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")

    #pass DB URL as a argument.
    engine = sa.create_engine(db_url)

    occdf.to_sql('occupations', engine, if_exists='replace', index=False)
    occtypedf.to_sql('occupationtype', engine, if_exists='replace', index=False)
    occtypedescdf.to_sql('occupationdesc', engine, if_exists='replace', index=False)
    titledf.to_sql('jobtitles', engine, if_exists='replace', index=False)
