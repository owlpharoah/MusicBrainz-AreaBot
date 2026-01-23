from config import * 
from fetch_SPARQL import *
from Wikidata import *
from MB import *
from Utils import *


#Sample: Rajasthan (Q1437)

#Step 1 - Fetch from Wikidata
print("Step 1")
wd_df = fetch_and_return(make_subdivision_query(TARGET,ALLOWED_INSTANCES))

#Step 2 - Fetch MB & Compare
print("Step 2")
mb_df = get_mb_areas_w_wikidata()
new_df = compare(wd_df,mb_df)

#Step 3 - Filter out actions and final output
print("Step 3")
creation_df , unresolved_df = process_hierarchy(new_df)

creation_df.to_csv('data/create.csv',index=False)
unresolved_df.to_csv('data/unresolved.csv',index=False)
