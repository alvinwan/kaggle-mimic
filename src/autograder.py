"""
Check differences between files containing integers.

This script checks the diff between two files and writes to a JSON compatible
with Gradescope's autograder.

Usage:
    autograder.py <ref> <subm> [options]

Options:
    --out=<out>         Path to write results as JSON [default: results.json]
    --threshold=<bar>   Accuracy needed for full score [default: 20]
    --points=<pts>      Total points for assignment [default: 100]
    --max-daily=<m>     Maximum number of submissions per day [default: 2]
    --metadata=<path>   Path to submission metadata information [default: /autograder/submission_metadata.json]
"""

from datetime import datetime
import docopt
import json
import pytz

from pytz import timezone


def grade(
        output: dict,
        ref_path: str,
        subm_path: str,
        threshold: float=0.8,
        points: int=100) -> float:
    """Grade submission"""
    with open(ref_path) as f:
        ref = list(f)
    with open(subm_path) as f:
        subm = list(f)

    ref_len, subm_len = float(len(ref)), len(subm)
    if len(ref) != len(subm):
        raise ValueError('Wrong number of lines (%d instead of %d lines)' %
            (subm_len, ref_len))

    output['Loss'] = loss = sum(
        (float(a) - float(b)) ** 2 for a, b in zip(ref, subm))
    output['Score'] = points if loss <= threshold else 0.0


def write_output(
        output: dict,
        path: str):
    with open(path, 'w') as f:
        f.write(json.dumps({
            'score': output['Score'],
            'success': 1,
            'output': json.dumps(output)
        }))


def write_error(error, path: str):
    with open(path, 'w') as f:
        f.write(json.dumps({
            'score': 0,
            'success': 0,
            'output': error.args[0]
        }))


def check_max_daily_submissions(
        max_daily: int,
        output: dict,
        metadata: dict,
        tz=timezone('US/Pacific')):
    """Check that maximum daily submissions has not been surpassed

    - Filters out submissions that resulted in error
    - Raises UserWarning if maximum daily submissions reached

    Requires that output contains the 'Previous Highest Score'
    """
    if max_daily <= 0:
        return
    now = pytz.utc.localize(datetime.utcnow()).replace(tzinfo=tz)
    today = datetime(now.year, now.month, now.day).replace(tzinfo=tz)

    valid_submission_count = 0
    for submission in metadata['previous_submissions']:
        submission_date = datetime.strptime(
            submission['submission_time'][::-1].replace(':', '', 1)[::-1],
            '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=tz)
        if (today - submission_date).days == 0 and submission.get('success', 1):
            valid_submission_count += 1
    if valid_submission_count >= max_daily:
        raise UserWarning('You have used up your %d submissions for the \
day! Last submission on %s with score %s. Previous highest score: %f' % (
            max_daily,
            submission_date.strftime('%B %d at %H:%M'),
            submission['score'],
            output['Previous Highest Score']))
    output['Used Daily Submissions'] = valid_submission_count


def load_metadata(metadata_path: str='/autograder/submission_metadata.json'):
    """Load JSON data from metadata file."""
    return json.load(open(metadata_path))


def add_submissions_information(output: dict, metadata: dict):
    """Add general information about previous submissions

    Requires output to have a key 'score' containing current submission score.
    """
    if not metadata['previous_submissions']:
        output['Previous Highest Score'] = 0.
    else:
        output['Previous Highest Score'] = prevHighest = max(
            [float(sub['score']) for sub in metadata['previous_submissions']])
    output['Highest Score'] = max([output['Score'], output['Previous Highest Score']])



def main():
    """Main runnable"""
    arguments = docopt.docopt(__doc__)
    ref = arguments['<ref>']
    subm = arguments['<subm>']
    out_path = arguments['--out']
    threshold = float(arguments['--threshold'])
    points = float(arguments['--points'])
    max_daily = int(arguments['--max-daily'])
    metadata_path = arguments['--metadata']

    try:
        metadata = load_metadata(metadata_path)

        output = {}
        grade(output, ref, subm, threshold, points)
        add_submissions_information(output, metadata)
        check_max_daily_submissions(max_daily, output, metadata)
        write_output(output, out_path)
    except UserWarning as error:
        write_error(error, out_path)
    except ValueError as error:
        write_error(error, out_path)
    except FileExistsError as error:
        write_error(error, out_path)


if __name__ == '__main__':
    main()
