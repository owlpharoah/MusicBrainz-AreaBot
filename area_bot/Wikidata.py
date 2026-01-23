from fetch_SPARQL import fetch_and_return
import pandas as pd




def make_subdivision_query(division_identifier: str,allowed_instance_qids: list[str],) -> str:
    """Generates a query"""

    allowed_instances = " ".join(f"wd:{qid}" for qid in allowed_instance_qids)

    return f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT
        
        ?area
        ?areaLabel
        ?parent
        ?parentLabel
        ?instance

    WHERE {{
        BIND(wd:{division_identifier} AS ?targetRegion)

        ?area wdt:P131* ?targetRegion .
        ?area wdt:P31 ?instance .

        VALUES ?instance {{ {allowed_instances} }}

        OPTIONAL {{ ?area wdt:P131 ?parent . }}
        OPTIONAL {{ ?area wdt:P17 ?country . }}
        OPTIONAL {{ ?area wdt:P1566 ?geonames . }}

        SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
        }}
    }}
    """

def get_parent_and_instance(qid) -> pd.DataFrame:
    """Fetches parent QID and the instance type of that parent"""
    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?label ?parent ?parentInstance WHERE {{
        BIND(wd:{qid} AS ?area)
        ?area rdfs:label ?label . FILTER(LANG(?label) = "en")
        OPTIONAL {{
            ?area wdt:P131 ?parent .
            OPTIONAL {{
                ?parent wdt:P31 ?pinst .
                BIND(STRAFTER(STR(?pinst), "entity/") AS ?parentInstance)
            }}
        }}
    }}
    LIMIT 1
    """
    try:
        res = fetch_and_return(query)
        return res.iloc[0].to_dict() if (res is not None and not res.empty) else None
    except Exception:
        return None
