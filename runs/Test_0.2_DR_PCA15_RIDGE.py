# Test_0.2_DR_PCA15_RIDGE.py
#
# Test size 0.2  |  PCA, 15 components  |  Ridge Regression (sheet #3)
#
# This is SGDC_60_40.py with the changes marked CHANGE below and nothing else.

import os
from pathlib import Path

# CHANGE 1: find the folder holding the three CSV files and run from there, so
# the plain file names below resolve no matter where this script is started
# from or how deeply it sits inside the project folder.
HERE = Path(__file__).resolve().parent
for PROJECT in [HERE, *HERE.parents]:
    if (PROJECT / 'Tuesday-WorkingHours.pcap_ISCX.csv').exists():
        os.chdir(PROJECT)
        break
else:
    raise SystemExit('Put this folder inside the folder that holds the three '
                     'CIC-IDS2017 CSV files, then run the script again.')
import numpy as np
import pandas as pd

df1 = pd.read_csv('Tuesday-WorkingHours.pcap_ISCX.csv', low_memory=True)
df2 = pd.read_csv('Wednesday-workingHours.pcap_ISCX.csv', low_memory=True)
df3 = pd.read_csv('Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv', low_memory=True)

dataset = pd.concat([df1, df2, df3], ignore_index=True)

dataset.columns = dataset.columns.str.strip()

# CHANGE 2: a stratified sample of 100000 flows, the same for every run.
# Gradient Boosting builds one tree per class per stage on a single core, so all
# 1.3 million flows would take hours per script. At least 50 flows of every
# class are kept, so the rare attacks stay in the split.
label = dataset.columns[-1]
dataset = pd.concat(
    [g.sample(n=min(len(g), max(50, round(100000 * len(g) / len(dataset)))), random_state=0)
     for _, g in dataset.groupby(label)],
    ignore_index=True
)

X = dataset.iloc[:, :-1]
y = dataset.iloc[:, -1]

X = X.apply(pd.to_numeric, errors='coerce')

X.replace([np.inf, -np.inf], np.nan, inplace=True)

from sklearn.impute import SimpleImputer

imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
X = imputer.fit_transform(X)

from sklearn.preprocessing import LabelEncoder

labelencoder_y = LabelEncoder()
y = labelencoder_y.fit_transform(y)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,   # CHANGE 3: test size
    random_state=0,
    stratify=y
)

# CHANGE 4: PCA, from PCA_LDA_KErnel_PCA_CODE.pdf (fit only on training data)
from sklearn.decomposition import PCA

pca = PCA(n_components=15)
X_train = pca.fit_transform(X_train)
X_test = pca.transform(X_test)

# CHANGE 5: Ridge Regression (sheet #3) in place of SGDClassifier
from sklearn.linear_model import Ridge

# Ridge is a regression model, used here exactly as the sheet writes
# it. Its numeric output is turned into a class after predict below.
classifier = Ridge(alpha=1.0)

classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test) 

# CHANGE 5b: Ridge predicts a number such as 3.4, not a class. Round it to the
# nearest class code and keep it inside the valid codes (0 to 10), so the
# confusion matrix and the scores below can be computed.
y_pred = np.clip(np.rint(y_pred), 0, len(labelencoder_y.classes_) - 1).astype(int)

from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report

cm = confusion_matrix(y_test, y_pred)

print("Confusion Matrix:\n")
print(cm)

print("\nAccuracy : {:.4f}".format(accuracy_score(y_test, y_pred)))
print("\nPrecision : {:.4f}".format(precision_score(y_test, y_pred, average='weighted')))
print("\nRecall : {:.4f}".format(recall_score(y_test, y_pred, average='weighted')))
print("\nF1 Score : {:.4f}".format(f1_score(y_test, y_pred, average='weighted')))

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# CHANGE 6: save the confusion matrix as Test_0.2_DR_PCA15_RIDGE.jpg and record the result
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

here = HERE                     # the folder this script sits in
names = [str(c) for c in labelencoder_y.classes_]
fig, ax = plt.subplots(figsize=(8, 7))
im = ax.imshow(cm, cmap='Blues', norm=LogNorm(vmin=1))
ax.set_xticks(range(len(names)), names, rotation=45, ha='right', fontsize=7)
ax.set_yticks(range(len(names)), names, fontsize=7)
ax.set_xlabel('Predicted')
ax.set_ylabel('True')
ax.set_title('Test_0.2_DR_PCA15_RIDGE   accuracy {:.4f}'.format(accuracy_score(y_test, y_pred)), fontsize=10)
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        if cm[i, j]:
            ax.text(j, i, cm[i, j], ha='center', va='center', fontsize=6,
                    color='white' if cm[i, j] > cm.max() / 3 else 'black')
fig.colorbar(im, ax=ax, fraction=0.04, label='flows (log scale)')
fig.tight_layout()
fig.savefig(here / 'Test_0.2_DR_PCA15_RIDGE.jpg', dpi=150)
plt.close(fig)

row = pd.DataFrame([{
    'Test': 0.2, 'DR': 'PCA15', 'Clas': 'RIDGE',
    'Acc': round(accuracy_score(y_test, y_pred), 4),
    'Pre': round(precision_score(y_test, y_pred, average='weighted'), 4),
    'Rec': round(recall_score(y_test, y_pred, average='weighted'), 4),
    'F1': round(f1_score(y_test, y_pred, average='weighted'), 4),
    'script': 'Test_0.2_DR_PCA15_RIDGE',
}])
# one file per run, so several scripts can run at the same time without
# overwriting each other. 21_run_45_mix.py merges them into the Excel sheet.
out = PROJECT / 'results' / 'parts_mix' / 'Test_0.2_DR_PCA15_RIDGE.csv'
out.parent.mkdir(parents=True, exist_ok=True)
row.to_csv(out, index=False)
