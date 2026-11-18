from __future__ import annotations

import json
from pathlib import Path
import platform

import joblib
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC


ROOT = Path(__file__).parent
DATA = ROOT / "data"
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"


def build_model(ngram_range=(2, 5), c=1.0):
    return Pipeline([
        ("features", FeatureUnion([
            ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), sublinear_tf=True, min_df=2, max_features=120_000)),
            ("char", TfidfVectorizer(analyzer="char", ngram_range=ngram_range, sublinear_tf=True, min_df=2, max_features=180_000)),
        ])),
        ("classifier", LinearSVC(C=c, class_weight="balanced", random_state=42)),
    ])


def read_split(path: Path):
    frame = pd.read_csv(path)
    required = {"message", "label"}
    if not required.issubset(frame.columns):
        raise ValueError(f"{path.name} phải có các cột {sorted(required)}")
    frame = frame.dropna(subset=["message", "label"]).copy()
    frame["message"] = frame["message"].astype(str).str.strip()
    frame["label"] = frame["label"].astype(int)
    frame = frame[frame.message.ne("")]
    if not set(frame.label.unique()).issubset({0, 1}):
        raise ValueError("Nhãn dữ liệu phải là 0=bình thường, 1=rác/lừa đảo.")
    return frame


def main():
    train = read_split(DATA / "train.csv")
    test = read_split(DATA / "test.csv")
    x_train, y_train = train.message, train.label
    x_test, y_test = test.message, test.label

    # Model selection uses training data only. The provided test split is touched once below.
    candidates = [
        ("char_3_5", (3, 5), 1.0),
        ("char_2_5", (2, 5), 1.0),
        ("char_3_6_c2", (3, 6), 2.0),
    ]
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_rows = []
    for name, ngrams, c in candidates:
        candidate = build_model(ngrams, c)
        scores = cross_validate(candidate, x_train, y_train, cv=folds,
                                scoring={"macro_f1": "f1_macro", "scam_recall": "recall"},
                                n_jobs=-1, return_train_score=False)
        cv_rows.append({"model": name, "char_ngram": str(ngrams), "C": c,
                        "cv_macro_f1_mean": float(scores["test_macro_f1"].mean()),
                        "cv_macro_f1_std": float(scores["test_macro_f1"].std()),
                        "cv_scam_recall_mean": float(scores["test_scam_recall"].mean())})
    cv_results = pd.DataFrame(cv_rows).sort_values(["cv_macro_f1_mean", "cv_scam_recall_mean"], ascending=False)
    winner = cv_results.iloc[0]
    selected = next(c for c in candidates if c[0] == winner.model)

    # Choose the operating threshold using out-of-fold training scores only.
    # Prefer recall while requiring at least 90% precision on those OOF predictions.
    selected_cv = build_model(selected[1], selected[2])
    oof_scores = cross_val_predict(selected_cv, x_train, y_train, cv=folds,
                                   method="decision_function", n_jobs=-1)
    threshold_rows = []
    for threshold in sorted(set(float(v) for v in oof_scores if v >= 0.0)):
        oof_pred = (oof_scores >= threshold).astype(int)
        precision = precision_score(y_train, oof_pred, pos_label=1, zero_division=0)
        recall = recall_score(y_train, oof_pred, pos_label=1, zero_division=0)
        if precision >= 0.90:
            threshold_rows.append((recall, precision, threshold))
    if threshold_rows:
        _, oof_precision, decision_threshold = max(threshold_rows)
    else:
        # Keep the original LinearSVC operating point when the precision target
        # cannot be met without lowering the threshold below zero.
        decision_threshold = 0.0
        oof_precision = 0.0

    model = build_model(selected[1], selected[2]).fit(x_train, y_train)
    test_scores = model.decision_function(x_test)
    predictions = (test_scores >= decision_threshold).astype(int)
    class_report = classification_report(y_test, predictions, labels=[0, 1],
                                         target_names=["legitimate", "scam"], output_dict=True, zero_division=0)
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1]).tolist()
    report = {
        "dataset_name": "Vietnamese Quality-Assured SMS Scam Dataset",
        "dataset_version": "Hugging Face main · train.csv/test.csv retrieved 2026-10-15",
        "license": "CC BY 4.0",
        "label_mapping": {"0": "legitimate", "1": "spam/scam"},
        "train_size": int(len(train)),
        "test_size": int(len(test)),
        "class_counts_train": {str(int(k)): int(v) for k, v in y_train.value_counts().sort_index().items()},
        "class_counts_test": {str(int(k)): int(v) for k, v in y_test.value_counts().sort_index().items()},
        "selected_model": {"name": selected[0], "char_ngram": str(selected[1]), "C": selected[2]},
        "decision_threshold": {"value": float(decision_threshold),
                               "selection": "OOF train: maximize scam recall subject to precision >= 0.90 and threshold >= 0",
                               "oof_scam_precision": float(oof_precision),
                               "target_scam_precision": 0.90},
        "cv_results": cv_results.to_dict(orient="records"),
        "metrics": {"accuracy": float((predictions == y_test).mean()),
                    "macro_f1": float(f1_score(y_test, predictions, average="macro")),
                    "scam_precision": float(precision_score(y_test, predictions, pos_label=1, zero_division=0)),
                    "scam_recall": float(recall_score(y_test, predictions, pos_label=1, zero_division=0)),
                    "scam_f1": float(f1_score(y_test, predictions, pos_label=1, zero_division=0))},
        "confusion_matrix": matrix,
        "classification_report": class_report,
        "software": {"python": platform.python_version(), "scikit_learn": sklearn.__version__},
        "seed": 42,
    }
    MODELS.mkdir(exist_ok=True)
    REPORTS.mkdir(exist_ok=True)
    joblib.dump(model, MODELS / "scam_classifier.joblib", compress=3)
    (REPORTS / "evaluation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    cv_results.to_csv(REPORTS / "cross_validation.csv", index=False)
    pd.DataFrame(matrix, index=["true_legitimate", "true_scam"], columns=["pred_legitimate", "pred_scam"]).to_csv(REPORTS / "confusion_matrix.csv")
    pd.DataFrame({"true_label": y_test.to_numpy(), "predicted_label": predictions.astype(int)}).to_csv(REPORTS / "test_predictions.csv", index=False)
    print(json.dumps({"selected_model": report["selected_model"], "decision_threshold": report["decision_threshold"], "metrics": report["metrics"],
                      "train_size": report["train_size"], "test_size": report["test_size"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
