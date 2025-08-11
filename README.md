# BraTS‑Unofficial‑Ranker

A lightweight, **unofficial** re‑implementation of the ranking procedure used in the BraTS challenges.  
Use it to score and rank your validation‑set submissions based on the statistics in the submission CSV files.

> **Heads‑up**  
> This code is wholly developed by us and **not** the reference implementation provided by the BraTS organizers.  
> Results produced may or may not match the official scores and carry **no official endorsement**.

---
## How the BraTS Ranking Works?


> The BraTS organizing committee internally evaluated each of the participating team’s automated segmentation models on the hidden test set of pre-operative meningioma cases to determine lesion-wise metrics for both DSC and 95HD for each of the three regions of interest. The participants were ranked against each other for each region of interest’s lesion-wise metric independently. A total of 6 independent rankings were calculated to reflect the two metrics, DSC and 95HD, for each of the ET, TC, and WT regions of interest. Then a “BraTS segmentation score” was calculated based on the average of each independent lesion-wise region of interest metric rankings. For example, if a team had the 3rd best ET DSC, 2nd best TC DSC, 3rd best WT DSC, 3rd best ET 95HD, 2nd best TC 95HD, and 4th best WT 95HD, then that team would have an average ranking of (3+2+3+3+2+4) / 6 = 2.83 as their BraTS segmentation score. The BraTS segmentation score was used to determine the final participant rankings relative to one another. 


LaBella D, Baid U, Khanna O, McBurney-Lin S, McLean R, Nedelec P, Rashid A, Tahon NH, Altes T, Bhalerao R, Dhemesh Y. Analysis of the BraTS 2023 intracranial meningioma segmentation challenge. arXiv preprint arXiv:2405.09787. 2024 May 16.

---
## How to use it?

1. Clone the repository
```bash
git clone https://github.com/Pediatric-Accelerated-Intelligence-Lab/BraTS‑Unofficial‑Ranker.git
cd BraTS‑Unofficial‑Ranker
```

2. Organize your submissions
```
BraTS‑Unofficial‑Ranker
│   README.md
│   ranker.py   
└───TaskName1
│       │   submission1.csv
│       │   submission2.csv
│       │   ...
```

3. Edit the `name_factory` in the `ranker.py`

4. run 
```bash
python ranker.py --task TaskName
```
