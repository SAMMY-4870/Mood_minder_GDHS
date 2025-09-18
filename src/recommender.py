import os
from typing import List, Dict, Any


_MODEL = None
_EMBEDDINGS_CACHE = {}


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    # Prefer sentence-transformers if available; otherwise try vanilla transformers
    try:
        from sentence_transformers import SentenceTransformer
        model_name = os.environ.get("REC_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        _MODEL = SentenceTransformer(model_name)
        return _MODEL
    except Exception:
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            model_name = os.environ.get("REC_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)

            def encode(texts: List[str]):
                inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
                with torch.no_grad():
                    outputs = model(**inputs)
                # mean pooling
                last_hidden = outputs.last_hidden_state
                attention_mask = inputs["attention_mask"].unsqueeze(-1)
                masked = last_hidden * attention_mask
                summed = masked.sum(dim=1)
                counts = attention_mask.sum(dim=1)
                emb = summed / counts
                return emb.cpu().numpy()

            class _Wrapper:
                def encode(self, texts):
                    return encode(texts)

            _MODEL = _Wrapper()
            return _MODEL
        except Exception:
            _MODEL = None
            return None


_CANDIDATES = [
    {"id": "quotes_transformers", "text": "Learn Transformers for quotes sentiment and generation", "url_name": "quotes"},
    {"id": "quotes_gpt", "text": "Try GPT-style text generation on quotes", "url_name": "quotes"},
    {"id": "images_vit", "text": "Explore Vision Transformers (ViT) for happy images", "url_name": "images"},
    {"id": "images_cnn", "text": "Classify images with CNNs and transfer learning", "url_name": "images"},
    {"id": "music_recs", "text": "Deep recommenders for music you love", "url_name": "music"},
    {"id": "games_rl", "text": "Reinforcement Learning via simple games", "url_name": "games"},
]


def _cos_sim(a, b):
    import numpy as np
    a = a / (np.linalg.norm(a) + 1e-9)
    b = b / (np.linalg.norm(b) + 1e-9)
    return float((a * b).sum())


def _embed_texts(texts: List[str]):
    model = _load_model()
    if model is None:
        return None
    # cache by joined hash to reduce recompute
    key = (id(model), tuple(texts))
    if key in _EMBEDDINGS_CACHE:
        return _EMBEDDINGS_CACHE[key]
    vecs = model.encode(texts)
    _EMBEDDINGS_CACHE[key] = vecs
    return vecs


def build_advanced_suggestions(db, email: str, url_for) -> List[Dict[str, Any]]:
    # Pull recent user activity
    if not email:
        return []
    recent = list(db.user_activity.find({"user_email": email}).sort("timestamp", -1).limit(200))
    texts = []
    for r in recent:
        parts = []
        action = r.get("action") or ""
        details = r.get("details") or ""
        parts.append(action)
        parts.append(details)
        texts.append(" ".join(parts))
    if not texts:
        return []

    # Embed user history and candidate suggestions
    user_vecs = _embed_texts(texts)
    if user_vecs is None:
        # model not available
        return []
    cand_texts = [c["text"] for c in _CANDIDATES]
    cand_vecs = _embed_texts(cand_texts)
    if cand_vecs is None:
        return []

    # Aggregate user profile as mean embedding
    import numpy as np
    profile = np.array(user_vecs).mean(axis=0)

    # Score candidates by cosine similarity
    scores = []
    for i, c in enumerate(_CANDIDATES):
        s = _cos_sim(profile, cand_vecs[i])
        scores.append((s, c))

    scores.sort(key=lambda x: x[0], reverse=True)

    # Build top-4 suggestions
    suggestions: List[Dict[str, Any]] = []
    for _, c in scores[:4]:
        suggestions.append({
            "text": c["text"],
            "url": url_for(c["url_name"]) if c.get("url_name") else "#",
        })
    return suggestions



