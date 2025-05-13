import re, argparse, pandas as pd, torch
from datasets import Dataset
from evaluate import load as load_metric
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)

LABELS = [
    "bonus",
    "deposit",
    "withdraw",
    "game_issue",
    "login_account",
    "anger_feedback",
    "other",
]

PATTERNS = {
    "bonus": r"bonus|freespin|cashback",
    "deposit": r"deposit|top.?up|add(ed)? funds?",
    "withdraw": r"withdra?w|cashout|payout",
    "game_issue": r"game|piggy|spin|slot",
    "login_account": r"log.?in|access|password|2fa|region|block",
    "anger_feedback": r"wtf|sucks?|scam|angry|mad",
}


def weak_label(msg: str) -> str:
    for lab, pat in PATTERNS.items():
        if re.search(pat, msg, re.I):
            return lab
    return "other"


def main(csv_path: str):
    print("🔹 reading CSV")
    df = pd.read_csv(csv_path)
    df["label"] = df["message"].apply(weak_label)

    label2id = {l: i for i, l in enumerate(LABELS)}
    id2label = {i: l for l, i in label2id.items()}

    ds = Dataset.from_pandas(df[["message", "label"]]).map(
        lambda x: {"label": label2id[x["label"]]}
    )

    tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")

    def tok_fn(batch):
        return tok(
            batch["message"],
            truncation=True,
            padding="max_length",        # ✅ simplest fix
            max_length=64,
        )

    ds = ds.map(tok_fn, batched=True)
    ds.set_format(
        type="torch",
        columns=["input_ids", "attention_mask", "label"],
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=len(LABELS),
        id2label=id2label,
        label2id=label2id,
    )

    args = TrainingArguments(
        output_dir="clf_ckpt",
        per_device_train_batch_size=16,
        num_train_epochs=3,
        learning_rate=2e-5,
        logging_steps=50,
        save_strategy="no",
    )

    metric = load_metric("accuracy")

    def compute(eval_pred):
        logits, labels = eval_pred
        return metric(
            predictions=logits.argmax(-1), references=labels
        )

    # OPTIONAL smarter collator (comment out if using padding="max_length")
    # collator = DataCollatorWithPadding(tokenizer=tok)

    trainer = Trainer(
        model,
        args,
        train_dataset=ds,
        compute_metrics=compute,
        # data_collator=collator,      # enable if you comment out padding="max_length"
    )

    print("🔹 training …")
    trainer.train()
    #acc = trainer.evaluate()["eval_accuracy"]
    #print(f"✅  finished – train accuracy ≈ {acc:.3f}")
    print(f"✅  finished – model trained")

    model.save_pretrained("distilbert-classifier")
    tok.save_pretrained("distilbert-classifier")
    print("📦 saved directory: distilbert-classifier/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    main(ap.parse_args().csv)
