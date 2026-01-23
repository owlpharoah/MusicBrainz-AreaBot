from MB import get_mb_areas_w_wikidata
from Wikidata import get_parent_and_instance
import pandas as pd
from config import *

#compares inputted dfs
def compare(wd_df,mb_df) -> pd.DataFrame:
    df_wikidata = wd_df
    df_wikidata['areaname_lower'] = df_wikidata['areaLabel'].str.lower()
    df_wikidata['qid'] = df_wikidata['area'].str.extract(r'/(Q\d+)$')
    df_wikidata['instance_qid'] = df_wikidata['instance'].str.extract(r'/(Q\d+)$')

    #mb
    df_mb = mb_df
    df_mb['qid'] = df_mb['wikidata_url'].str.extract(r'/(Q\d+)$')

    existing_qid = set(df_mb['qid'].dropna().unique())
    existing_names = set(df_mb['name_lower'].dropna().unique())

    def check_status(row):
        wd_qid = row['qid']
        wd_name = row['areaname_lower']
        
        if wd_qid in existing_qid:
            return 'skipped'
        
        if wd_name in existing_names:
            return 'Review'
            
        return 'continue'

    df_wikidata['status'] = df_wikidata.apply(check_status, axis=1)
    print(f'WD: {len(df_wikidata)}')
    print(f'Skipped: ',{(df_wikidata["status"] == 'skipped').sum()})
    print(f'Review: ',{(df_wikidata["status"] == 'Review').sum()})
    print(f'continue: ',{(df_wikidata["status"] == 'continue').sum()})

    return df_wikidata


def process_hierarchy(new_df) -> list[pd.DataFrame]:
    known_qids = set(new_df[new_df["status"] == "skipped"]["qid"].dropna().unique())
    candidates = new_df[new_df["status"] != "skipped"]
    creation_queue = []
    unresolved = []

    for _, row in candidates.iterrows():
        start_qid = row["qid"]
        if start_qid in known_qids:
            continue

        temp_stack = []
        pointer_qid = start_qid
        visited = set()
        resolved = False
        current_branch_depth = 0

        print(f"\nAnalyzing: {row.get('areaLabel', start_qid)}")

        while pointer_qid and pointer_qid not in known_qids:
            if pointer_qid in visited:
                print(f"  [!] Circular reference at {pointer_qid}")
                break
            visited.add(pointer_qid)

            data = get_parent_and_instance(pointer_qid)
            if not data:
                break

            parent_uri = data.get("parent")
            parent_qid = str(parent_uri).split("/")[-1] if pd.notna(parent_uri) else None
            parent_instance = data.get("parentInstance")

            if parent_instance in ROOT_INSTANCES or parent_qid in known_qids:
                temp_stack.append({
                    "qid": pointer_qid,
                    "name": data["label"],
                    "parent_qid": parent_qid,
                    "instance": parent_instance
                })
                resolved = True
                print(f"Linked {data['label']} to: {parent_qid}")
                break

            if current_branch_depth >= MAX_DEPTH:
                print(f"WARNING: Hierarchy too deep ({current_branch_depth}+ steps). Needs human review")
                break

            if parent_instance in SKIPPED_INSTANCES:
                print(f"  [Climbing] Skipping historical/invalid node: {parent_qid}")
                pointer_qid = parent_qid
                continue

            temp_stack.append({
                "qid": pointer_qid,
                "name": data["label"],
                "parent_qid": parent_qid,
                "instance": parent_instance
            })
            print(f"  [Step {current_branch_depth+1}] Added {data['label']} (Parent: {parent_qid})")
            pointer_qid = parent_qid
            current_branch_depth += 1

        # Commit to the final queue if we found a path to a root/known area
        if resolved:
            
            while temp_stack:
                item = temp_stack.pop()
                if item["qid"] not in known_qids:
                    creation_queue.append(item)
                    known_qids.add(item["qid"])
        else:
            unresolved.append({
                "qid": start_qid,
                "name": row.get('areaLabel'),
                "reason": "Depth Exceeded / Unresolvable"
            })

    return pd.DataFrame(creation_queue), pd.DataFrame(unresolved)

