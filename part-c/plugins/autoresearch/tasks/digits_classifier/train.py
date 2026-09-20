"""
AutoResearch task: classify handwritten digits (sklearn's load_digits).

Contract: print "METRIC: <float>" to stdout — the harness never reads
anything else about this file. Higher is better (validation accuracy).

This baseline is deliberately weak (a single shallow decision tree, no
scaling, no tuning) so an optimization loop has obvious room to improve it.
"""
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesClassifier

X, y = load_digits(return_X_y=True)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=0)

model = ExtraTreesClassifier(n_estimators=200, random_state=0)
model.fit(X_train, y_train)
accuracy = model.score(X_val, y_val)

print(f"METRIC: {accuracy}")