import re
import os
import sys
import csv
import json
import logging
import hashlib
import uuid
from datetime import datetime, timezone
import subprocess
import multiprocessing
from collections import defaultdict
import argparse
from pathlib import Path
import networkx as nx
# from networkx.drawing.nx_agraph import write_dot
# from networkx.drawing.nx_pydot import write_dot

from . import spdx30 as spdx


class SPDXGraph(nx.Graph):

    def __init__(self, objectset):
        super().__init__()
        self.objectset = objectset
        self.id_to_idx = {}
        self.idx_to_id = {}
        self.labels = {}

        for o in objectset.foreach():
            self.add_object(o)

    def get_idx(self, id, label=None):
        if id not in self.id_to_idx:
            idx = len(self.id_to_idx)
            self.id_to_idx[id] = idx
            self.idx_to_id[idx] = id
            return idx
        else:
            return self.id_to_idx[id]
    
    def set_label(self, idx, label):
        self.labels[idx] = label

    def get_id(self, idx):
        return self.idx_to_id[idx]

    def add_relationship(self, r):
        logging.debug(f"adding relationship {r}")
        f = r.from_
        fidx = self.get_idx(f)
        ts = r.to
        for t in ts:
            tidx = self.get_idx(t)
            self.add_edge(fidx, tidx, key=r.relationshipType)

    def add_object(self, o):
        logging.debug(f"adding {o}")
        idx = self.get_idx(id)
        self.add_node(idx)

        # switch on class of o
        if isinstance(o, spdx.Element):
            self.set_label(idx, o.name)
            self.add_edge(idx, self.get_idx(o.creationInfo), key='creationInfo')

            if isinstance(o, spdx.Relationship):
                self.add_relationship(o)

        return idx

def main():
    parser = argparse.ArgumentParser(
                    prog='spdx3_to_graph',
                    description='create a visualization of SPDX 3.0 documents',)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('spdx', type=Path)


    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"args: {args}")
    logging.info(f"Processing {args.spdx}")

    objectset = spdx.SHACLObjectSet()
    with args.spdx.open("r") as f:
        d = spdx.JSONLDDeserializer()
        d.read(f, objectset)

    # if args.verbose:
    #     spdx.print_tree(objectset.objects)

    G = SPDXGraph(objectset)
    if args.verbose:
        logging.debug(f"Graph: {G}")

    nx.write_graphml(G, f"{args.spdx}.graphml")
    # nx.write_dot(G, f"{args.spdx}.dot")
