# Five Classifiers with PCA on CIC-IDS2017

Advanced Computer Networks course project. Forty-five runs of the base code,
`SGDC_60_40.py`, over three test sizes, three PCA component counts and five
classifiers, with a confusion matrix and a metric row for every run.

## What is here

| Path | Contents |
|---|---|
| `SGDC_60_40.py` | The base code the 45 scripts are derived from, unchanged. |
| `runs/Test_<test>_DR_PCA<n>_<clf>.py` | 45 run scripts. |
| `runs/Test_<test>_DR_PCA<n>_<clf>.jpg` | 45 confusion matrices, one per run. |
| `results/45_runs_formatted.xlsx` | The results sheet. |
| `paper/` | The research paper, as Word and PDF. |
| `requirements.txt` | Package versions. |

## The grid

| Varies | Values |
|---|---|
| Test size | 0.2, 0.4, 0.6 |
| PCA components | 5, 10, 15 |
| Classifier | GB (#8), MLP (#18), RF (#7), QDA (#17), RIDGE (#3) |

3 x 3 x 5 = 45. The classifier numbers refer to the course reference sheet.

The MLP and Random Forest are used exactly as the sheet writes them. Three
need a word:

- **Gradient Boosting** (#8) gets `random_state=0`. The sheet leaves the seed
  unset. The trees then break ties between equally good splits at random, so
  a rerun of the same script gives different numbers. The first, unseeded
  run of `Test_0.2_DR_PCA10_GB.py` scored 93.38% accuracy; with
  `random_state=0` it scores 97.63%. With the seed every run is
  repeatable.
- **QDA** (#17) gets `solver='eigen', shrinkage=0.1`. Heartbleed has 11 flows
  in the whole dataset, so at most settings it has fewer training flows than
  PCA components and its covariance matrix cannot be estimated. As the sheet
  writes it, QDA stops with a `LinAlgError` on 7 of the 9 settings.
- **Ridge** (#3) is a regression model. It predicts a number such as 3.4
  rather than a class, so its prediction is rounded to the nearest class code
  and kept between 0 and 10.

PCA is unsupervised, so it never sees the labels and has no limit tied to the
number of classes.

## How a run script differs from the base code

Every script is `SGDC_60_40.py` with six changes (seven for Ridge) and nothing
else. Each one is marked with a `CHANGE n` comment in the file, so any script
can be read against the base code line by line.

1. Walk up the folders until the three CSVs are found and run from there, so
   the CSV names in the base code resolve from any depth.
2. A stratified sample of 100,000 flows, the same for every run, with a floor of
   50 flows per class. Gradient Boosting fits one tree per class per stage on a
   single core, which is 1,100 trees for 11 classes. The floor keeps the rare
   attacks in the split: Heartbleed has 11 flows in the whole dataset.
3. The test size: 0.2, 0.4 or 0.6, in place of the fixed 0.4.
4. PCA, fitted on the training split only, with `n_components` varied per run.
5. The classifier, in place of `SGDClassifier`.
   5b. Ridge only: round the prediction to the nearest class code.
6. Save the confusion matrix as `<script name>.jpg` and write one row for the
   results sheet.

Everything else is as it was: the same three captures, `str.strip()` on the
column names, `to_numeric(errors='coerce')`, infinities to NaN, mean imputation,
`LabelEncoder`, `train_test_split(random_state=0, stratify=y)` and the same six
metric prints with weighted averages. Like the base code, nothing scales the
features before PCA.

## Data

[CIC-IDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) from the Canadian
Institute for Cybersecurity. Three captures are used, which give 11 classes:

| Capture | Attacks |
|---|---|
| Tuesday | FTP-Patator, SSH-Patator |
| Wednesday | DoS Hulk, GoldenEye, slowloris, Slowhttptest, Heartbleed |
| Thursday morning | Web Attack: Brute Force, XSS, SQL Injection |

The CSVs are not included here. Download `MachineLearningCSV.zip` from the
dataset page and put these three files in the project folder:

```
Tuesday-WorkingHours.pcap_ISCX.csv
Wednesday-workingHours.pcap_ISCX.csv
Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
```

## Running it

```bash
pip install -r requirements.txt
python runs/Test_0.2_DR_PCA5_RF.py
```

Each script is standalone and writes its own jpg and its own row. Every script
seeds its random parts (`random_state=0`, or `random_state=42` for the MLP as
the sheet writes it), so a rerun reproduces the same numbers.

## Reading the sheet

`results/45_runs_formatted.xlsx` has five tabs:

- **Legend**: every short form spelled out, with what each column means
- **45 runs**: one row per run, Test size through F1 score
- **full detail**: the same rows with the script that produced each one
- **best per classifier**: highest F1 per classifier
- **components x classifier**: F1 averaged over the three test sizes

The last two tabs are built from formulas, so correcting a number in **full
detail** updates them.

Precision, recall and F1 are weighted averages, as in the base code. Weighting by
class size means benign traffic dominates, so a model can score well on this
sheet while missing the rare attacks. The confusion matrices show where that
happens.

## Results

Weighted F1, averaged over the three test sizes:

| Classifier | PCA5 | PCA10 | PCA15 |
|---|---|---|---|
| GB (#8) | 0.9623 | 0.8825 | 0.9700 |
| MLP (#18) | 0.6081 | 0.7393 | 0.6813 |
| RF (#7) | 0.9861 | 0.9900 | **0.9906** |
| QDA (#17) | 0.3339 | 0.3328 | 0.3347 |
| RIDGE (#3) | 0.8595 | 0.8600 | 0.8612 |

Best run per classifier, with the macro F1 from the classification report:

| Classifier | Test | DR | Acc | Pre | Rec | F1 | Macro F1 |
|---|---|---|---|---|---|---|---|
| RF | 0.2 | PCA15 | 0.9920 | 0.9919 | 0.9920 | 0.9919 | 0.83 |
| GB | 0.2 | PCA15 | 0.9784 | 0.9784 | 0.9784 | 0.9780 | 0.70 |
| RIDGE | 0.6 | PCA15 | 0.8656 | 0.8794 | 0.8656 | 0.8617 | 0.17 |
| MLP | 0.4 | PCA10 | 0.8379 | 0.8434 | 0.8379 | 0.7914 | 0.13 |
| QDA | 0.2 | PCA5 | 0.2446 | 0.9224 | 0.2446 | 0.3458 | 0.20 |

### What the numbers show

Only the two tree ensembles do the job. Random Forest reaches 0.9920 accuracy and finds nearly every attack class. Gradient Boosting reaches 0.9784 but is less even: it finds 69% of SSH-Patator and 75% of DoS slowloris. Both lose most on the three web attacks, which have only a few dozen test flows between them and look alike in their flow statistics.

Ridge and the MLP look acceptable on this sheet and are not. Benign traffic is 79.5% of the test flows, so labelling everything benign already scores 0.7945 accuracy. Ridge gets 0.8656 by recognising benign traffic and part of DoS Hulk and almost nothing else (macro F1 0.17). The MLP is unstable: its accuracy ranges from 0.3986 to 0.8379 and even its best run finds little beyond benign traffic (macro F1 0.13).

QDA is the opposite case. Its accuracy stays between 0.2286 and 0.2446 because it labels most benign flows as attacks, yet it catches many of the rare attacks, so its macro F1 (0.20) beats Ridge and the MLP.

### Why: the features are not scaled before PCA

The base code feeds the raw features to PCA. Flow durations in microseconds and byte rates are millions of times larger than flag counts, so the first components follow a few large-valued features and sit on very different scales. Trees do not mind, because they split one input at a time. The other three do, but not all for that reason alone.

A separate check (not one of the 45 runs) repeated test 0.2 with PCA10 after standardising the features:

| Classifier | Raw Acc | Raw macro F1 | Standardised Acc | Standardised macro F1 |
|---|---|---|---|---|
| RF | 0.9914 | 0.81 | 0.9957 | 0.80 |
| MLP | 0.7975 | 0.09 | 0.9830 | 0.71 |
| RIDGE | 0.8626 | 0.16 | 0.7878 | 0.15 |
| QDA | 0.2364 | 0.22 | 0.6259 | 0.29 |

The raw rows match the sheet exactly, which confirms the check uses the same pipeline. Standardising rescues the MLP and lifts QDA, though QDA stays far behind because its one-Gaussian-per-class model fits the traffic poorly. Ridge gets worse: its problem is regressing on class codes, which no scaling repairs.
