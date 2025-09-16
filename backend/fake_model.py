import random

def fake_predict(comment):
    is_bot = int("http" in comment or "win" in comment.lower() or "subscribe" in comment.lower())
    confidence = round(random.uniform(0.7, 0.99), 2) if is_bot else round(random.uniform(0.6, 0.95), 2)
    return {
        "comment": comment,
        "is_bot": is_bot,
        "confidence": confidence
    }
