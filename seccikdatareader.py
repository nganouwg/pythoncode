
import os
import json
import pandas as pd
import sqlalchemy as sa
import csv

from collections import Counter
from utils import json_inspector as ji

'''
"cik": 1750,
"entityName": "AAR CORP",
"facts": {
    "dei": {
        "EntityCommonStockSharesOutstanding": {
            "label": "Entity Common Stock, Shares Outstanding",
            "description": "Indicate number of shares or other units outstanding of each of registrant's classes of capital or common stock or other ownership interests, 
                            if and as stated on cover of related periodic report. Where multiple classes or units exist define each class/interest by adding class of stock 
                            items such as Common Class A [Member], Common Class B [Member] or Partnership Interest [Member] onto the Instrument [Domain] of the Entity Listings, 
                            Instrument.",
            "units": {
                "shares": [
                    {
                        "end": "2010-08-31",
                        "val": 39662816,
                        "accn": "0001104659-10-049632",
                        "fy": 2011,
                        "fp": "Q1",
                        "form": "10-Q",
                        "filed": "2010-09-23",
                        "frame": "CY2010Q3I"
                    }
'''

"""
Recursively traverse a nested JSON structure.

Args:
    data: The JSON data (dict or list) to traverse.
    prefix: Optional string to prefix keys with.
"""
'''
For example:
    cik: 1750,
    entityName: "AAR CORP"
    facts.dei.EntityCommonStockSharesOutstanding.label: "Entity Common Stock, Shares Outstanding"
    facts.dei.EntityCommonStockSharesOutstanding.description: "Indicate number of shares or other units outstanding ...."
    facts.dei.EntityCommonStockSharesOutstanding.units.shares.end: "2010-08-31"
    facts.dei.EntityCommonStockSharesOutstanding.units.shares.val: 39662816
    facts.dei.EntityCommonStockSharesOutstanding.units.shares.accn: "0001104659-10-049632"
'''

#TODO: Segment the results at a specific level to create a list. e.g level 3 "facts.dei.EntityCommonStockSharesOutstanding"
def traverse_json(data, prefix=""):

    results = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            if isinstance(value, (dict, list)):
                traverse_json(value, new_prefix)
            else:
                results.append(f"{new_prefix}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            traverse_json(item, f"{prefix}[{i}]")

    return results


"""
    Get maximum number of levels
    Counts the levels of nesting in a JSON object.
"""
def count_levels(data, level=1):
    
    if isinstance(data, dict):
        max_level = level
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                max_level = max(max_level, count_levels(value, level + 1))
        return max_level
    elif isinstance(data, list):
        max_level = level
        for item in data:
            if isinstance(item, (dict, list)):
                max_level = max(max_level, count_levels(item, level + 1))
        return max_level
    else:
        return level
    

"""
    Recursively extract all keys from a nested JSON object, including their prefixes.

    :param data: The JSON object to extract keys from
    :param prefix: The current prefix for nested keys
    :param result: A set to store the key paths
    :return: A set of key paths
"""
'''
    cik, entityName, facts
    facts.us-gaap, etc
'''
#TODO: 
#   Handle duplicates, for example if every level 3 object like "facts.dei.EntityCommonStockSharesOutstanding" has a "label" key
#   find a way to represent that without replication 
#   like "facts.dei.EntityCommonStockSharesOutstanding.label, "facts.dei.EntityPublicFloat.label". 
#   In other words, show that label can be used as a variable in a dataframe. 
def extract_keys(data, prefix="", result=None):
    
    if result is None:
        result = set()

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            result.add(new_prefix)
            extract_keys(value, new_prefix, result)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_prefix = f"{prefix}[{i}]"
            extract_keys(item, new_prefix, result)

    return result

"""
    Extract keys from a nested JSON object at a specific level, including parent hierarchy.

    :param data: The JSON object to extract keys from
    :param target_level: The specific level to extract
    :param level: The current level in the hierarchy
    :param parent: The parent key for nested keys
    :param result: A list to store the key paths
    :return: A dictionary with levels as keys and their corresponding key paths
"""
'''
    Level 0: 
        cik, entityName, facts
    Level 1: 
        facts.dei, etc...
    level 2: 
        facts.dei.EntityCommonStockSharesOutstanding, etc...
    Level 3: 
        facts.dei.EntityCommonStockSharesOutstanding.label, 
        facts.dei.EntityCommonStockSharesOutstanding.description, 
        facts.dei.EntityCommonStockSharesOutstanding.units
    Level 4: 
        facts.dei.EntityCommonStockSharesOutstanding.units.shares, etc.
    Level 5: 
        facts.dei.EntityCommonStockSharesOutstanding.units.shares.end, 
        facts.dei.EntityCommonStockSharesOutstanding.units.shares.val, 
        facts.dei.EntityCommonStockSharesOutstanding.units.shares.accn, etc.
'''
def extract_keys_at_level(data, target_level, level=0, parent="", result=None):
    
    if result is None:
        result = []

    if level == target_level:
        if isinstance(data, dict):
            result.extend([f"{parent}.{key}" if parent else key for key in data.keys()])
        elif isinstance(data, list):
            result.extend([f"{parent}[{i}]" for i in range(len(data))])
        return result

    if isinstance(data, dict):
        for key, value in data.items():
            new_parent = f"{parent}.{key}" if parent else key
            extract_keys_at_level(value, target_level, level + 1, new_parent, result)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_parent = f"{parent}[{i}]" if parent else f"[list item {i}]"
            extract_keys_at_level(item, target_level, level + 1, new_parent, result)

    return result


"""
    Flatten the JSON data up to a specific level using pandas.json_normalize,
    excluding nested dict or list objects beyond the specified level.

    :param data: The JSON object to flatten
    :param max_level: The maximum level to flatten
    :return: A flattened DataFrame
"""
def flatten_json_keys(data, max_level):

    df = pd.DataFrame(columns=["FactTitle", "Factname"])
    
    # Flatten the JSON with max_level
    df1 = pd.json_normalize(
        data,
        max_level=max_level,
        sep='.'  # Separator for nested keys
    )

    #  Remove columns where values are dicts or lists
    for col in df1.columns:
        if any(isinstance(value, (dict, list)) for value in df1[col]):
            keys = col.split(".")
            df.loc[len(df)] = [keys[1], keys[2]]
            df1.drop(columns=col, inplace=True)

    df['key'] = 1
    df1['key'] = 1

    results = pd.merge(df, df1, on = 'key')
    results.drop(columns='key', inplace=True)

    return results


def flatten_json_values_with_keys(data, keys: list[str]):

    results = pd.DataFrame()

    for k in keys:
        sk = k.split(".")
        df1 = pd.json_normalize(data[sk[0]][sk[1]][sk[2]], max_level=0)
        df1.drop(columns='units', inplace=True)
        df1["FactTitle"] = sk[1]
        df1["Factname"] = sk[2]
        results = pd.concat([results, df1], ignore_index=True)

    return results


"""
    Pivot wide columns into rows based on a list of prefixes.

    :param df: The DataFrame to reshape
    :param pivot_columns_prefixes: A list of prefixes of the columns to pivot (e.g., ['facts.dei', 'facts.us-gaap'])
    :return: A reshaped DataFrame
"""
def pivot_columns_to_rows(df, pivot_columns_prefixes):
    
    # Filter columns to pivot based on all prefixes
    columns_to_pivot = [col for col in df.columns if any(col.startswith(prefix) for prefix in pivot_columns_prefixes)]

    # Keep the other columns as identifiers
    id_columns = [col for col in df.columns if col not in columns_to_pivot]

    # Melt the DataFrame
    reshaped_df = pd.melt(df, id_vars=id_columns, value_vars=columns_to_pivot,
                          var_name='Attribute', value_name='Value')
    return reshaped_df


"""
    Extract detailed data for each child of the specified fact prefix
    into individual DataFrames with the desired structure.

    :param data: The JSON object to process
    :param fact_prefix: The prefix to extract children from (e.g., 'facts.dei')
    :return: A dictionary of DataFrames, one for each child
"""
def extract_fact_data(data, fact_prefix):
    
    fact_dataframes = {}

    # Navigate to the specified fact prefix
    facts = data
    for key in fact_prefix.split('.'):
        facts = facts.get(key, {})

    # Process each child
    for fact_name, fact_details in facts.items():
        units = fact_details.get('units', {})
        for unit_type, records in units.items():
            df = pd.DataFrame(records)
            df['UnitType'] = unit_type
            fact_dataframes[f"{fact_prefix}.{fact_name}"] = df

    return fact_dataframes



with open("/Users/georgesnganou/Documents/Projects/Data/Security_and_Exchange_Commission/20240711/companyfacts/CIK0000001750.json") as file:

    data = json.loads(file.read())

    ####################################### Data Inspection ##########################################
    #traverse_json(data)

    #max_level = count_levels(data)
    #print(max_level)

    #results = extract_keys(data)
    #print(results)

    #results = extract_keys_at_level(data, 2)
    #print(results)

    #flat = ji.traverse_json(data, "cik")
    #print(flat)

    #with open('/Users/georgesnganou/Documents/Projects/Data/Security_and_Exchange_Commission/20240711/jsonInspectorRaw.csv', 'w', newline='') as csvfile:
        #fieldname = ['level', 'prefix', 'type']
        #writer = csv.DictWriter(csvfile,fieldnames=fieldname)

        #writer.writeheader()
        #writer.writerows(flat)


    #summary = ji.traverse_json_keys(flat)
    #print(summary)
    #summary_file = '/Users/georgesnganou/Documents/Projects/Data/Security_and_Exchange_Commission/20240711/jsonInspectorSummary.csv'
    #summary.to_csv(summary_file, index=False)

    ####################################### ################### ##########################################

    
    
    leve2keys = extract_keys_at_level(data, 2)
    df2 = flatten_json_values_with_keys(data, leve2keys)

    #print(df2)

    words = []
    shortlabels = []

    for value in df2['label']:
        shortlabels = shortlabels + value.split(',')
        words = words + value.replace(',', "").split(" ")

    #print(shortlabels)
    #print(words)

    w_counter = Counter(words)
    sl_counter = Counter(shortlabels)

    #print(w_counter)
    #print(sl_counter)

    dfwc = pd.DataFrame.from_dict(w_counter, orient='index', columns=['count']).reset_index()
    dfwc.rename(columns={'index': 'word'}, inplace=True)
    dfwc = dfwc.sort_values(by='count', ascending=False)
    #print(dfwc)
    #cikwordfile = '/Users/georgesnganou/Documents/Projects/Data/Security_and_Exchange_Commission/20240711/cik_words.csv'
    #dfwc.to_csv(cikwordfile, index=False)

    dfslc = pd.DataFrame.from_dict(sl_counter, orient='index', columns=['count']).reset_index()
    dfslc.rename(columns={'index': 'word'}, inplace=True)
    dfslc = dfslc.sort_values(by='count', ascending=False)
    #print(dfslc)
    #cikslfile = '/Users/georgesnganou/Documents/Projects/Data/Security_and_Exchange_Commission/20240711/cik_shortlabels.csv'
    #dfslc.to_csv(cikslfile, index=False)

    

    '''
    df1 = flatten_json_keys(data, 2)
    print(df1)

    leve2keys = extract_keys_at_level(data, 2)
    df2 = flatten_json_values_with_keys(data, leve2keys)

    dfs = []
    fact_prefixes = ['facts.dei', 'facts.us-gaap']

    for fact_prefix in fact_prefixes:
        fact_dataframes = extract_fact_data(data, fact_prefix)
        for fact_name, df in fact_dataframes.items():
            df["factname"] = fact_name
            dfs.append(df)
    
    df3 = pd.concat(dfs)

    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")

    engine = sa.create_engine(db_url)

    df1.to_sql('cik', engine, if_exists='replace', index=False)
    df2.to_sql('factdescs', engine, if_exists='replace', index=False)
    df3.to_sql('units', engine, if_exists='replace', index=False)
    '''

