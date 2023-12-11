import pickle
import xgboost
import os
import sys
import pandas as pd
import re
import numpy as np
import tempfile
from metrics import bleu, edit_distance, exact_match, kv_match
from metrics import kv_wildcard

module_dict = {
    'KV_MTH': kv_match,
    'EDT_DIST': edit_distance,
    'KV_WLD': kv_wildcard,
    'BLEU': bleu,
    'ECT_MTH': exact_match
}

def test(result_str="", reference_str=""):
    score_dict_temp = {}
    for metric_name, module in module_dict.items():
        try:
            score_dict_temp[metric_name] = [module.test(result_str, reference_str)]
        except Exception as e:
            score_dict_temp[metric_name] = [0]
    df_X = pd.DataFrame(score_dict_temp)
    with open('metrics/unit_test_pred.pkl', 'rb') as file:
        model_loaded = pickle.load(file)
    output = model_loaded.predict(df_X)
    result = (output >= 0.5).astype(int)
    return result.tolist()[0]