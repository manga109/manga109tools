# manga109tools-dev
manga109tools is a helper for datasets with the format of Manga109 annotation. This tool provides commands for the validation of the format of annotations for now.

## Validation
Validate the XML files of annotations

### Manga109 Dataset
1. Download this package
```
pip install git+https://github.com/manga109/manga109tools.git
```

2. Validate the Manga109 dataset
```bash
cd /path/to/manga109_dir
manga109tools validate
```

You can specify the annotation directory using a `--target_annot` argument.
The choices are currently `annotations`, `annotations.v2018.05.31`, `annotations.v2020.12.18`.
We use `annotations` as a default argument.

We also provide a `--root_dir` argument to run this command without changing the current directory.

### You Own Dataset with the Format of Manga109 Annotation
1. You can copy `~/.manga109tools/exceptions.yaml` to any path to prepare the yaml file for each your own dataset. We refer to the path as `/path/to/exceptions.yaml`.

2. Edit `/path/to/exceptions.yaml` to specify exceptions for the validation.

The below is the default content of `exceptions.yaml` for Manga109. The keys are the names of test functions and the values are the exceptions for each test function.
```yaml
# list of two ids
# the bounding box of the element of the first id contains that of the second id
test_duplicate_bbox: []

# list of two ids
# the face of the first id contains the face of the second id
test_face_not_in_face:
# ByebyeC-BOY id="0000eeca" contains "0000eedb"
- 
  - 0000eeca
  - 0000eedb
# ByebyeC-BOY id="0000ff7d" contains "0000ff77"
- 
  - 0000ff7d
  - 0000ff77
# DualJustice id="00012d20" contains "00012d27"
-
  - 00012d20
  - 00012d27
```

3. Validate your own dataset

```bash
cd /path/to/your_own_dataset
manga109tools validate --exception_path /path/to/exceptions.yaml
```

## For Developers
* We format codes with `black`.
* We use docstring in a google format.
