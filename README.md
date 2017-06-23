# Kaggle Mimic on Gradescope
Gradescope Autograder that mimics Kaggle, minus a lengthy approval process and leaderboards. This repository operates under the assumption that (1) you wish to keep student's scores private (2) students receive full credit for accuracies above some threshold, and (3) you don't want to wait for Kaggle to approve your contest.

# Usage

To use the autograder, navigate to the repository's `src/`. We will call `$KM_ROOT` the repository root.

```
cd $KM_ROOT/src
```

Zip all files in `src/`.

```
zip autograder.zip *
```

Upload this zip file to a new Gradescope programming assignment's autograder. See [Gradescope's Autograder Documentation](https://gradescope-autograders.readthedocs.io/en/latest/) for more information.

# Configure

To set options available through the Python script's CLI, modify the provided bash script `src/run_autograder`. Otherwise, the Python script `src/autograder.py` is run on every assignment.
