"""
Train a TF-IDF + LinearSVC model using the CSV.
After running, drop `model.pkl` into app/services and change classifier_service to load it.
"""
import pickle, re, argparse, pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

CAT_RULES = {  # same rules as before
    "bonus":  r"bonus|freespin|cashback",
    "deposit": r"deposit|depo|top.?up|add(ed)? funds?",
    "withdraw": r"withdra?w|cashout|payout",
    "login": r"log.?in|access issues?|password|2fa",
    "angry": r"sucks?|wtf|scam|angry|mad",
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    def rule(msg):
        for cat, pat in CAT_RULES.items():
            if re.search(pat, msg, re.I):
                return cat
        return "other"
    df["label"] = df["message"].apply(rule)
    X, y = df["message"], df["label"]

    clf = make_pipeline(
        TfidfVectorizer(min_df=3, ngram_range=(1,2)),
        LinearSVC()
    ).fit(X, y)

    with open("model.pkl", "wb") as f:
        pickle.dump(clf, f)
    print("Saved model.pkl with accuracy:", clf.score(X, y))
