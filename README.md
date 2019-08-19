# FollowUp Dataset

Recent work on Natural Language Interfaces to Databases (NLIDB) has attracted considerable attention. NLIDB allow users to search databases using natural language instead of SQL-like query languages. While saving the users from having to learn query languages, multi-turn interaction with NLIDB usually involves multiple queries where contextual information is vital to understand the users' query intents. In this paper, we address a typical contextual understanding problem, termed as follow-up query analysis. Our work summarizes typical follow-up query scenarios and provides the new `FollowUp` dataset with 1000 query triples on 120 tables.

## Citation

If you use FollowUp, please cite the following work. Our paper is also avaiable on [arxiv](https://arxiv.org/abs/1901.08259).
> Qian Liu, Bei Chen, Jian-Guang Lou, Ge Jin and Dongmei Zhang. FANDA: A Novel Approach to Perform Follow-­‐up Query Analysis. In AAAI 2019.

```
@inproceedings{qian2019aaai,
  title={FANDA: A Novel Approach to Perform Follow-­‐up Query Analysis},
  author={Qian Liu, Bei Chen, Jian-Guang Lou, Ge Jin and Dongmei Zhang},
  booktitle={AAAI},
  year={2019}
}
```

## Evaluation

You could easily evalute your model output on FollowUp dataset following our `eval.py` script. Put your model prediction (as format of string) case by case under the file `predict.example`, then run the `eval.py` as following:

```
python eval.py
```

You will get the evalution result on `test.tsv`. For example, the example prediction result will get the result of:

```shell
================================================================================
                     FollowUp Dataset Evaluation Result
================================================================================
BLEU Score:  100.00 (%)
Symbol Acc:  100.00 (%)
```

## Tables

**tables.jsonl**: store the table information, and every line(table) is a json format object. `header` means the column names, `types` means the types inherited from [WikiSQL](https://github.com/salesforce/WikiSQL), `id` indicates the table ids origination in WikiSQL, `rows` are the values of whole table. A line looks like the following:

```json
{
	"header": [
		"Date",
		"Opponent",
		"Venue",
		"Result",
		"Attendance",
		"Competition"
	],
	"page_title": "2007–08 Guildford Flames season",
	"types": [
		"real",
		"text",
		"text",
		"text",
		"real",
		"text"
	],
	"page_id": 15213262,
	"id": [
		"2-15213262-12",
		"2-15213262-7"
	],
	"section_title": "March",
	"rows": [
		[
			"6",
			"Milton Keynes Lightning",
			"Away",
			"Lost 3-5 (Lightning win 11-6 on aggregate)",
			"537",
			"Knockout Cup Semi-Final 2nd Leg"
		],
		[
			"8",
			"Romford Raiders",
			"Home",
			"Won 7-3",
			"1,769",
			"League"
		],
		...
		[
			"28",
			"Chelmsford Chieftains",
			"Away",
			"Won 3-2",
			"474",
			"Premier Cup"
		]
	],
	"caption": "March"
}
```


## Content

**train.tsv** and **test.tsv**: train/test split of FollowUp Dataset. Every line is a tuple of format (Precendent Query, Follow-up Query, Fused Query, Table ID), where the *Table ID* is **line index** starting from 1 in `tables.jsonl`. Split symbol is TAB(\t). A line looks like the following:

```tsv
how many champions were there, according to this table?	show these champions for different all-star game.	show champions for different all-star game.	74
```


## Concat

If you have any question or have difficulity in applying your model on the FollowUp dataset, please feel free to concat me: qian.liu AT buaa dot edu dot cn. Sure, you could also create a new issue and I will tackle them as soon as possible.
