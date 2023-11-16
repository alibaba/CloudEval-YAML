import difflib

def test(result_str="", reference_str=""):
    result_seq = result_str.strip().splitlines()
    reference_seq = reference_str.strip().splitlines()
    # strip each line
    result_seq = [line.strip() for line in result_seq]
    reference_seq = [line.strip() for line in reference_seq]
    diff = list(difflib.Differ().compare(result_seq, reference_seq))

    additions = sum(1 for line in diff if line.startswith('+ '))
    deletions = sum(1 for line in diff if line.startswith('- '))

    edit_ratio = (additions + deletions) / len(reference_seq)
    return max(1 - edit_ratio, 0)

