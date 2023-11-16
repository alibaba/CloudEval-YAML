from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction
# import sacrebleu

def test(result_str="", reference_str=""):
    reference_tokens = reference_str.split()
    result_tokens = result_str.split()

    # 4-gram BLEU by default, needs at least 4 tokens
    try:
        assert len(reference_tokens) >= 4
    except:
        print(f"Invalid reference code:\n{reference_str}")
        return 0
    
    if len(result_tokens) < 4:
        return 0
    
    # treat the whole context as a single sentence
    score = corpus_bleu([[reference_tokens]], [result_tokens], weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=SmoothingFunction().method3)
    # sacrebleu_score = sacrebleu.corpus_bleu([result_str], [[reference_str]])
    return score
