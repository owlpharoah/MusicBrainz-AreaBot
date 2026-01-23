from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

SPARQL = SPARQLWrapper(
    "https://query.wikidata.org/sparql", agent="MusicBrainz-AreaBot/0.0"
)


def fetch_query(query: str) -> dict:
    try:
        SPARQL.setQuery(query)
        SPARQL.setReturnFormat(JSON)
        results = SPARQL.query().convert()
        return results

    except Exception as e:
        print(e)
        return None


def to_df(results: dict) -> pd.DataFrame:
    try:
        results_df = pd.json_normalize(results["results"]["bindings"])
        results_df = results_df[
            [col for col in results_df.columns if col.endswith("value")]
        ]
        results_df.columns = [col.split(".")[0] for col in results_df.columns]
        return results_df

    except Exception as e:
        print(e)
        return None


def to_csv(df: pd.DataFrame, filename: str) -> str:
    path = f"../data/{filename}"
    try:
        df.to_csv(filename, index=False)
        return path

    except Exception as e:
        print(e)
        return None


def fetch_and_store(query: str, filename: str) -> str:
    results = fetch_query(query)
    df = to_df(results)
    path = to_csv(df, filename)

    return path

def fetch_and_return(query: str):
    results = fetch_query(query)
    df = to_df(results)

    return df
