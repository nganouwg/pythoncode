
import pandas as pd

'''
class jsonmember:
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level
        self.parent_names = set()
        self.children_names = set()

    @property
    def add_parent(self, value):
        self.parent_names.add(value)

    @property
    def add_child(self, value):
        self.children_names.add(value)
    
    def __str__(self):
        return f"{self.name} p{len(self.parent_names)} - c{len(self.children_names)}"
    

class jsontree:
    def __init__(self, jsonmembers: list[jsonmember], depth: int):
        self.jsonmembers = jsonmembers 
        self.depth = depth

    @property
    def depth(self):
        return self.depth
'''  
    
def traverse_json(data: dict, prefix="", level=0):

    results = []

    if isinstance(data, dict):
        results.append({"level": level, "prefix": prefix, "type": "dict"})
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            if isinstance(value, (dict, list)):
                results = results + traverse_json(value, new_prefix, level + 1)
            else:
                results.append({"level": level + 1, "prefix": new_prefix, "type": type(value)})
    elif isinstance(data, list):
        results.append({"level": level, "prefix": prefix, "type": "list"})
        for i, item in enumerate(data):
            results = results + traverse_json(item, f"{prefix}[{i}]", level + 1)

    return results


#We are going to create a column for each level
#for each key count the number of parent and children [parent:children]
'''
    curparentkey
    prevparentkey
    skip the first element -- using python slicing myslit[i:]
    For each record in the list
    
        getlevel(x)
        getprefix

        if column level(x) doesn't exist
            add column x

        split the prefix with '.'
        get key at prefix[level(x)]
        set curparentkey = prefix[level(x-1)]
        if key already exist at column level(x)
            Increment parent count
            if curparentkey == prevparentkey
                Increment parent's child count
        else 
            add element to df[column] 
            with 1 parent and no kids
'''
def traverse_json_keys(data: list[dict]):

    sorted_data = sorted(data, key=lambda x: (x['level']))

    depth=None

    df = pd.DataFrame()

    curparentkey = None
    prevparentkey = None

    for rec in sorted_data[1:]:

        #print(rec)
        
        level = f'level_{rec["level"]}'
        pos = rec["level"]
        prefix = rec["prefix"].replace("[", ".No_Name_Key_").replace("]", "")

        if level not in df.columns:
            df.insert(pos-1, level, '')

        p = prefix.split('.')
        key = p[pos]
        curparentkey = p[pos-1]
        
        if key in df[level].values:
            #increment parents and/or children counts
            pass
        else:
            df.loc[len(df), level] = key

    return df
