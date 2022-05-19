from datetime import datetime
import csv
from elasticsearch import Elasticsearch, helpers
import ir_datasets
import pandas as pd

if __name__ == "__main__":
    es = Elasticsearch(host = "localhost", port = 9200)

    query_text=' '

    bool_query = {
    "size": 10000,
    "query": {
    "bool": {
    "should": [
    {"match": {"Content": query_text}}
    ]
    ,"minimum_should_match": 1,
    "boost": 1.0
    }
    }
    }


    res = es.search(index='clinical', body={
            "query": {
                "match_all": {}
            }
        })

    print(res)