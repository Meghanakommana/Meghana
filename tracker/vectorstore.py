# tracker/vectorstore.py

import numpy as np
import json
import os
import logging
from sklearn.neighbors import NearestNeighbors
import tracker.config as config

TEXT_DIM = 384

class SimpleVectorStore:
    def __init__(self, path=config.EMBEDDINGS_PATH):
        self.npy = path + ".npy"
        self.json = path + ".json"
        self.vectors = np.empty((0, TEXT_DIM))
        self.map = {}
        self.index = None
        self._load()

    def _load(self):
        if os.path.exists(self.npy) and os.path.exists(self.json):
            try:
                self.vectors = np.load(self.npy)
                with open(self.json) as f:
                    self.map = json.load(f)
            except Exception:
                self._reset()
        else:
            self._reset()
        self._rebuild()

    def _reset(self):
        self.vectors = np.empty((0, TEXT_DIM))
        self.map = {}

    def _rebuild(self):
        if len(self.vectors) == 0:
            self.index = None
            return
        self.index = NearestNeighbors(metric="cosine")
        self.index.fit(self.vectors)

    def upsert(self, path, vec):
        if vec.shape[0] != TEXT_DIM:
            return

        if path in self.map:
            self.vectors[self.map[path]] = vec
        else:
            self.map[path] = len(self.vectors)
            self.vectors = np.vstack([self.vectors, vec])

        np.save(self.npy, self.vectors)
        with open(self.json, "w") as f:
            json.dump(self.map, f)
        self._rebuild()

    def query(self, vec, top_k=5):
        if not self.index:
            return []

        vec = vec.reshape(1, -1)
        dists, idxs = self.index.kneighbors(vec, min(top_k, len(self.vectors)))
        inv = {v: k for k, v in self.map.items()}
        return [
            {"path": inv[i], "score": float(1 - d)}
            for d, i in zip(dists[0], idxs[0])
        ]
    def get_vector(self, path):
        idx = self.map.get(path)
        if idx is None:
            return None
        return self.vectors[idx]