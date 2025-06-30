import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load toxicity model once
tokenizer = AutoTokenizer.from_pretrained("unitary/toxic-bert")  
model     = AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")

def run(messages: list, run_id=None):
    # Get threshold from env, default to 0.1
    threshold = float(os.getenv("TOXICITY_THRESHOLD", 0.1))

    # Tokenize batch
    inputs = tokenizer(
        [m["text"] for m in messages],
        return_tensors="pt",
        padding=True,
        truncation=True
    )
    with torch.no_grad():
        logits = model(**inputs).logits
        probs  = torch.sigmoid(logits).tolist()

    results = []
    for m, p in zip(messages, probs):
        toxic_score = p[1]  # label 1 = toxicity probability
        action = "allow" if toxic_score < threshold else "delete"
        results.append({
            "id":    m["id"],
            "action":action,
            "score": toxic_score
        })

    return {"moderation": results}
