import logging
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

from tracker.metadata_db import MetadataDB
from tracker.embedder import Embedder
from tracker.vectorstore import SimpleVectorStore
from tracker.query_parser import parse_query

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

db = MetadataDB()
embedder = Embedder()
vstore = SimpleVectorStore()

# ---------------- HEALTH ----------------
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# ---------------- FILE LIST ----------------
@app.route("/get_all_files", methods=["GET"])
def get_all_files():
    return jsonify(db.get_all_files())


@app.route("/get_recent_files", methods=["GET"])
def get_recent_files():
    return jsonify(db.get_recent_files())


@app.route("/mark_accessed", methods=["POST"])
def mark_accessed():
    data = request.json or {}
    path = data.get("path")
    if path:
        db.increment_access_count(path)
    return jsonify({"status": "ok"})


# ---------------- 🔥 INTENT SEARCH ----------------
@app.route("/search", methods=["POST"])
def search():
    data = request.json or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"results": []})

    filters = parse_query(query)
    logging.info(f"PARSED → {filters}")

    # 1️⃣ SQL FILTER
    results = db.search_by_metadata(filters)

    if not results:
        return jsonify({"results": []})

    # 2️⃣ SEMANTIC RANK (optional but powerful)
    if filters["semantic"]:
        q_vec = embedder.embed_text(filters["semantic"])

        scored = []

        for r in results:
            vec = vstore.get_vector(r["path"]) if hasattr(vstore, "get_vector") else None

            if vec is not None:
                score = float(np.dot(q_vec, vec))
            else:
                score = 0.0

            r["score"] = round(score, 3)
            scored.append(r)

        scored.sort(key=lambda x: x["score"], reverse=True)
        results = scored

    return jsonify({"results": results[:20]})


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(port=5000, debug=False)
