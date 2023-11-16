import loader
import prompt
import query
import json
import ray
import os
import openai
import time
import importlib
import sys
import random
from tqdm import tqdm
from metrics import bleu, edit_distance, exact_match, kv_match
from metrics import kv_wildcard, unit_test

metric_map = {
    'bleu': bleu,
    'edit_distance': edit_distance,
    'exact_match': exact_match,
    'kv_match': kv_match,
}

def import_module_from_string(module_name, module_code):
    module_spec = importlib.util.spec_from_loader(module_name, loader=None)
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    exec(module_code, module.__dict__)
    return module


def evaluate(config):

    problem_keys = json.loads(loader.read_memory(config, 'problem_keys'))

    if 'Kubernetes' in config['libs'] and config['metrics']['unit_test']:
        # restart minikube
        print("Preparing minikube for unit tests ...")
        unit_test.run_bash('minikube delete && minikube start && sleep 20')

    for problem_key in tqdm(problem_keys, desc='Evaluating'):
        reference_code = loader.read_memory_problem(config, problem_key, f'reference_code')
        unit_test_code = loader.read_memory_problem(config, problem_key, f'unit_test_code')
        if unit_test_code is not None:
            unit_test_code = unit_test_code
        
        scores_dict = {}
        for metric_name in config['metrics'].keys():
            scores_dict[metric_name] = []

        for sample_id in range(config['num_samples']):
            generated_code = loader.read_memory_problem(config, problem_key, f'generated_code_{sample_id}')
            
            for metric_name in config['metrics'].keys():
                if config['metrics'][metric_name]:
                    # if the metric is enabled
                    if metric_name in metric_map.keys():
                        # general scoring
                        score = metric_map[metric_name].test(generated_code, reference_code)
                    # problem-specific scoring
                    elif metric_name == 'kv_wildcard':
                        try:
                            score = kv_wildcard.test(generated_code, reference_code)
                        except Exception as e:
                            # raise Exception(f"Error occurred while calculating kv_wildcard : {str(e)}")
                            score = 0
                    elif metric_name == 'unit_test':
                        if unit_test_code is not None:
                            score, unit_test_output = unit_test.test(generated_code, unit_test_code, problem_key, config)
                            loader.write_memory_problem(config, problem_key, f'unit_test_output_{sample_id}', unit_test_output)
                            loader.log_unit_test_output(config, problem_key, sample_id)
                        else:
                            score = 0
                    else:
                        raise Exception(f'Unknown metric: {metric_name}')
                    scores_dict[metric_name].append(score)
                else:
                    scores_dict[metric_name].append(-1)
        
        for metric_name in config['metrics'].keys():
            loader.write_memory_problem(config, problem_key, f'{metric_name}_scores', json.dumps(scores_dict[metric_name]))

def calc_scores(config):

    problem_keys = json.loads(loader.read_memory(config, 'problem_keys'))

    # exp scores for calculation only
    exp_scores = {}
    for metric_name in config['metrics'].keys():
        if config['metrics'][metric_name]:
            exp_scores[metric_name] = 0

    # calc per problem scores
    for problem_key in problem_keys:
        problem_scores_summary = ""
        problem_scores_summary += f'------ Problem: {problem_key} ------\n'
        for metric_name in config['metrics'].keys():
            if config['metrics'][metric_name]:
                if metric_name == 'unit_test' and not loader.read_memory_problem(config, problem_key, f'unit_test_code'):
                    problem_scores_summary += f'{metric_name} score: N/A\n'
                else:
                    scores = json.loads(loader.read_memory_problem(config, problem_key, f'{metric_name}_scores'))
                    problem_scores_summary += f'{metric_name} score: {sum(scores):.2f} / {config["num_samples"]}\n'
                    exp_scores[metric_name] += sum(scores)
        print(problem_scores_summary)
        loader.write_memory_problem(config, problem_key, f'scores_summary', problem_scores_summary)

    return calc_exp_scores(config)

# main
def calc_exp_scores(config):

    problem_keys = json.loads(loader.read_memory(config, 'problem_keys'))

    # exp scores for calculation
    exp_scores = {}
    for metric_name in config['metrics'].keys():
        if config['metrics'][metric_name]:
            exp_scores[metric_name] = {
                'numerator': 0,
                'denominator': 0
            }

    # category scores for calculation
    category_scores = {}
    for lib in config['libs']:
        for mode in config['modes']:
            category_name = f'{lib}_{mode}'
            category_scores[category_name] = {}
            for metric_name in config['metrics'].keys():
                if config['metrics'][metric_name]:
                    category_scores[category_name][metric_name] = {
                        'numerator': 0,
                        'denominator': 0
                    }

    # calc per problem scores
    for problem_key in problem_keys:
        category_name = f"{problem_key.split('_')[0]}_{problem_key.split('_')[1]}"
        for metric_name in config['metrics'].keys():
            if config['metrics'][metric_name]:
                if metric_name == 'unit_test' and not loader.read_memory_problem(config, problem_key, f'unit_test_code'):
                    pass
                else:
                    scores = json.loads(loader.read_memory_problem(config, problem_key, f'{metric_name}_scores'))
                    category_scores[category_name][metric_name]['numerator'] += sum(scores)
                    category_scores[category_name][metric_name]['denominator'] += len(scores)
                    exp_scores[metric_name]['numerator'] += sum(scores)
                    exp_scores[metric_name]['denominator'] += len(scores)

    # calc per category scores
    for lib in config['libs']:
        for mode in config['modes']:
            category_name = f'{lib}_{mode}'
            category_exist = False
            category_scores_summary = f'------ Category: {category_name} ------\n'
            for metric_name in config['metrics'].keys():
                if config['metrics'][metric_name]:
                    numerator = category_scores[category_name][metric_name]["numerator"]
                    denominator = category_scores[category_name][metric_name]["denominator"]
                    category_scores_summary += f'{metric_name} score: {numerator:.2f} / {denominator}\n'
                    if denominator > 0:
                        category_exist = True
            
            if not category_exist:
                continue
            print(category_scores_summary)
            loader.write_memory(config, f'{category_name}_scores_summary', category_scores_summary)

    # calc exp scores
    exp_scores_summary = f'------ Overall --- Model: {config["model"]} ------\n'
    exp_scores_summary += f'Dataset: {config["question_type"]} ({len(problem_keys)} problems)\n'
    # exp_scores_summary += f'Number of problems: {len(problem_keys)}\n'
    for metric_name in config['metrics'].keys():
        if config['metrics'][metric_name]:
            numerator = exp_scores[metric_name]["numerator"]
            denominator = exp_scores[metric_name]["denominator"]
            normalized_numerator = numerator / denominator
            exp_scores_summary += f'{metric_name} score: {numerator:.2f} / {denominator}\n'
            # exp_scores_summary += f'{metric_name} score: {normalized_numerator:.3f}\n'

    print(exp_scores_summary)
    loader.write_memory(config, 'exp_scores_summary', exp_scores_summary)
    return exp_scores
