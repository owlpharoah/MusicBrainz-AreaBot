from config import * 
from fetch_SPARQL import *
from Wikidata import *
from MB import *
from Utils import *


try:

    
    print("\n[Step 1] Fetch from Wikidata")
    wd_df = fetch_and_return(make_subdivision_query(TARGET,ALLOWED_INSTANCES))

    
    print("\n[Step 2] Fetch MB & Compare")
    mb_df = get_mb_areas_w_wikidata()
    new_df = compare(wd_df,mb_df)

    
    print("\n[Step 3] Filter out actions and final output")
    creation_df , unresolved_df = process_hierarchy(new_df)

    creation_df.to_csv('data/create.csv',index=False)
    unresolved_df.to_csv('data/unresolved.csv',index=False)
except TimeoutError as e:
    print(" [ERROR] {e} ") 
