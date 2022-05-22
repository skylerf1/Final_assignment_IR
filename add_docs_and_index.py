from datetime import datetime
import csv
from elasticsearch import Elasticsearch, helpers
import ir_datasets
import pandas as pd
import sys


def filterKeys(document):
    return {key: document[key] for key in use_these_keys}


def doc_generator(df, index_name):
    for index, document in df.iterrows():
        if index % 1000 == 0:
            sys.stdout.write('\rAdded {:10d} documents'.format(index))

        yield {
            "_index": index_name,
            "_id": f"{document['doc_id']}",
            "_source": filterKeys(document),
        }
    raise StopIteration


if __name__ == "__main__":

    es = Elasticsearch(host="localhost", port=9200)

    request_body = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            }
        },
        "mappings": {
            "properties": {
                "content": {
                    "type": "text",
                    "fielddata": True,
                    "term_vector": "with_positions_offsets_payloads",
                    "store": True,
                    "analyzer": "whitespace"
                }
            }
        }
    }

    if es.indices.exists('clinical'):
        es.indices.delete('clinical')
        print('Index already exists')
    es.indices.create('clinical', body=request_body)
    print('Created Index')

    dataset = ir_datasets.load("clinicaltrials/2021")

    df = pd.DataFrame(dataset.docs_iter())

    df["content"] = df['title'].astype(str) + " " + df["summary"].astype(str) + " " + df['detailed_description'].astype(
        str) + " " + df['eligibility']

    df["content"] = df["content"].replace('\n', '', regex=True)
    df['content'] = df["content"].replace('\r', '', regex=True)

    use_these_keys = ['content']

    helpers.bulk(es, doc_generator(df, 'clinical'))
