import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from pathlib import Path
from datasets import load_dataset
from swarm_dynamics import ROOT_PATH


RAW_PATH = ROOT_PATH / "datastore" / "raw"
MOLTBOOK_RAW = RAW_PATH / 'moltbook'
HF_MOLTBOOK = 'SimulaMet/moltbook-observatory-archive'

def main():

    MOLTBOOK_RAW.mkdir(parents=True, exist_ok=True)

    files = ['posts', 'agents', 'comments', 'snapshots', 'submolts']

    for file in files:
        pass
        #print('Loading ', file '...\n')
        #ds = load_dataset(HF_MOLTBOOK, file)
        #pq.write_table(ds, MOLTBOOK_RAW / f'{file}.parquet')

    print('Loading word frequencies...\n')
    ds = load_dataset(HF_MOLTBOOK, 'word_frequency')
    print(ds)
    # df = ds.set_format(type='pandas')
    # df.to_csv(MOLTBOOK_RAW / 'word_frequency.csv', index=False)


if __name__ == '__main__':
    main()