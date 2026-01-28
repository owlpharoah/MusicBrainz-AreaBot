import pandas as pd
import sqlalchemy as sa
from config import PG_HOST,PG_DATABASE,PG_PASSWORD,PG_PORT,PG_USER

#gets all areas in mb with wikidata
def get_mb_areas_w_wikidata() -> pd.DataFrame :

    sa_conn_str = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
    engine = sa.create_engine(sa_conn_str)

    with engine.connect() as conn:
        query = '''
        SELECT 
            a.name, 
            u.url AS wikidata_url
        FROM area a
        LEFT JOIN l_area_url lau ON a.id = lau.entity0
        LEFT JOIN url u ON lau.entity1 = u.id
        LEFT JOIN link l ON lau.link = l.id
        LEFT JOIN link_type lt ON l.link_type = lt.id AND lt.gid = '85c5256f-aef1-484f-979a-42007218a1c2'
        '''
        df_musicbrainz = pd.read_sql(sa.text(query), conn)

    df_musicbrainz['name_lower'] = df_musicbrainz['name'].str.lower()
    print(f'MB: {len(df_musicbrainz)}')
    return df_musicbrainz
