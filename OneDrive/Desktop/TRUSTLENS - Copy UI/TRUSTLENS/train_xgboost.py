import pandas as pd
import joblib

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

from xgboost import XGBClassifier

# Load data
df = pd.read_csv("results/fusion_features.csv")

X = df.drop(columns=["filename", "label"])
y = df["label"]

# Encode labels
encoder = LabelEncoder()
y = encoder.fit_transform(y)
print(encoder.classes_)
# 5-Fold Cross Validation
skf = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

accuracies = []

fold = 1

for train_idx, test_idx in skf.split(X, y):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y[train_idx]
    y_test = y[test_idx]

    model = XGBClassifier(
        n_estimators=40,
        max_depth=3,
        learning_rate=0.15,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    acc = accuracy_score(y_test, pred)

    accuracies.append(acc)

    print(f"\nFold {fold}")
    print("Accuracy:", round(acc, 4))
    print(classification_report(y_test, pred))

    fold += 1

# Train final model on all data
final_model = XGBClassifier(
    n_estimators=40,
    max_depth=3,
    learning_rate=0.15,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

final_model.fit(X, y)

joblib.dump(final_model, "models/xgboost_model.pkl")

print("\n============================")
print("Average Accuracy:", round(sum(accuracies)/len(accuracies), 4))
print("============================")
print("Model saved successfully!")