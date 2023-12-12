import json
from pathlib import Path
import os
import yaml
from tqdm import tqdm
import shutil

file_key_map = {
    "question.txt": "question",
    "labeled_code.yaml": "reference_code",
    "unit_test.sh": "unit_test_code",
    "question_translated.txt": "question_translated",
    "question_simplified.txt": "question_simplified",
    "question_simplified_translated.txt": "question_simplified_translated",
}

def load_config(config_path):
    config = json.load(open(config_path))
    if 'all' in config["models"]:
        config["models"] = config["available_models"]
    if 'all' in config["question_types"]:
        config["question_types"] = config["available_question_types"]
    if 'all' in config["libs"]:
        config["libs"] = config["available_libs"]
    if 'all' in config["modes"]:
        config["modes"] = config["available_modes"]
    if config['self_validation']:
        config['num_samples'] = 1
        config['models'] = ['self_validation'] + config['models']
    return config

def load_dataset(config):
    """
    Load question, reference_code into memory.
    """

    clean_memory(config)
    write_memory(config, 'config', json.dumps(config))
    source_dir = config["source_dir"]
    output_dir = config["output_dir"]
    exp = config["exp"]
    libs = config["libs"]
    modes = config["modes"]
    problems_to_include = config["problems_to_include"]
    problems_to_exclude = config["problems_to_exclude"]
    problem_keys = []
    for lib in libs:
        for mode in modes:
            source_path = Path(source_dir) / lib / mode
            if not source_path.exists():
                continue
            folder_list = os.listdir(source_path)
            problems = sorted([p for p in folder_list if p.startswith('q')], key=lambda x: float(str(x).replace("q", "")))
            for problem in problems:
                problem_key = f'{lib}_{mode}_{problem}'
                if 'all' not in problems_to_include and problem_key not in problems_to_include:
                    continue
                if problem_key in problems_to_exclude:
                    continue
                problem_dir = source_path / problem
                unit_test_found = False
                # traverse all files in the problem folder
                for root, _, files in os.walk(problem_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_key = os.path.relpath(file_path, problem_dir)
                        if file_key in file_key_map:
                            # critical file
                            if file_key == "unit_test.sh":
                                unit_test_found = True
                            file_key = file_key_map[file_key]
                        else:
                            # context file
                            file_key = 'context_' + file_key

                        with open(file_path, "r") as f:   
                            content = f.read()
                            write_memory_problem(config, problem_key, f'{file_key}', content)
                            write_memory_problem(config, problem_key, f'output_dir', str(Path(output_dir) / exp / lib / mode / problem))
                if not unit_test_found:
                    print(f'Unit test not found for {problem_key}')
                problem_keys.append(f'{problem_key}')
    write_memory(config, 'problem_keys', json.dumps(problem_keys))

def save_generated_codes(config):
    """
    Save generated codes into output_dir.
    """

    problem_keys = json.loads(read_memory(config, 'problem_keys'))
    for problem_key in problem_keys:
        output_dir = read_memory_problem(config, problem_key, f'output_dir')
        os.makedirs(output_dir, exist_ok=True)
        for sample_id in range(config['num_samples']):
            generated_code = read_memory_problem(config, problem_key, f'generated_code_{sample_id}')
            if generated_code is None:
                generated_code = ''
                write_memory_problem(config, problem_key, f'generated_code_{sample_id}', generated_code)
            else:
                generated_code = generated_code
            with open(f'{output_dir}/generated_code_{sample_id}.txt', 'w') as f:
                f.write(generated_code)

def load_generated_codes(config):
    """
    Load generated codes from output_dir into memory.
    """

    problem_keys = json.loads(read_memory(config, 'problem_keys'))
    for problem_key in problem_keys:
        output_dir = read_memory_problem(config, problem_key, f'output_dir')
        for sample_id in range(config['num_samples']):
            with open(f'{output_dir}/generated_code_{sample_id}.txt', 'r') as f:
                generated_code = f.read()
                write_memory_problem(config, problem_key, f'generated_code_{sample_id}', generated_code)

def use_reference_codes(config):
    """
    Use reference code as generated code
    """

    problem_keys = json.loads(read_memory(config, 'problem_keys'))
    for problem_key in problem_keys:
        reference_code = read_memory_problem(config, problem_key, f'reference_code')
        for sample_id in range(config['num_samples']):
            write_memory_problem(config, problem_key, f'generated_code_{sample_id}', reference_code)

def save_scores(config, output_filename='exp_output.txt'):
    """
    Save scores into output_dir.
    """

    problem_keys = json.loads(read_memory(config, 'problem_keys'))
    exp_output_dir = Path(config['output_dir']) / config['exp']
    os.makedirs(exp_output_dir, exist_ok=True)
    f_exp = open(f'{exp_output_dir}/{output_filename}', 'w')
    for problem_key in problem_keys:
        output_dir = read_memory_problem(config, problem_key, f'output_dir')
        os.makedirs(output_dir, exist_ok=True)

        problem_scores_details = "\nDetails:\n"
        # read detailed scores
        for metric_name in config['metrics']:
            if config['metrics'][metric_name]:
                metric_scores_details = read_memory_problem(config, problem_key, f'{metric_name}_scores')
                problem_scores_details += f'{metric_name}: {metric_scores_details}\n'
        
        # read summary if exists
        problem_scores_summary = read_memory_problem(config, problem_key, f'scores_summary')
        if problem_scores_summary is not None:
            problem_scores_summary = problem_scores_summary

            with open(f'{output_dir}/scores.txt', 'w') as f:
                f.write(problem_scores_details)
                f.write(problem_scores_summary)
            f_exp.write(problem_scores_summary)

    for lib in config['libs']:
        for mode in config['modes']:
            category_name = f'{lib}_{mode}'
            category_scores_summary = read_memory(config, f'{category_name}_scores_summary')
            if category_scores_summary is not None:
                category_scores_summary = category_scores_summary
                f_exp.write(category_scores_summary)

    exp_scores_summary = read_memory(config, f'exp_scores_summary')
    if exp_scores_summary is not None:
        exp_scores_summary = exp_scores_summary
    else:
        exp_scores_summary = "\nSummary not available, please run evaluate.summarize_exp_scores(config) before saving scores\n"
    f_exp.write(exp_scores_summary)
    f_exp.close()



def save_prompts(config):
    """
    Save prompts into output_dir.
    """

    problem_keys = json.loads(read_memory(config, 'problem_keys'))
    for problem_key in problem_keys:
        output_dir = read_memory_problem(config, problem_key, f'output_dir')
        os.makedirs(output_dir, exist_ok=True)
        prompt = read_memory_problem(config, problem_key, f'prompt')
        with open(f'{output_dir}/prompt.txt', 'w') as f:
            f.write(prompt)

def log_unit_test_output(config, problem_key, sample_id):
    """
    Log unit test output into output_dir.
    """

    output_dir = read_memory_problem(config, problem_key, f'output_dir')
    os.makedirs(output_dir, exist_ok=True)
    unit_test_output = read_memory_problem(config, problem_key, f'unit_test_output_{sample_id}')
    with open(f'{output_dir}/unit_test_output_{sample_id}.txt', 'w') as f:
        f.write(unit_test_output)

def summarize_overall_scores(config, question_type_scores_list):
    for metric_name in config['metrics'].keys():
        if config['metrics'][metric_name]:
            question_num = sum([question_type_scores[metric_name]['denominator'] for question_type_scores in question_type_scores_list])
            break
    
    overall_scores_summary = f"====== Overall === Model: {config['model']} ======\n"
    overall_scores_summary += f"Dataset: {', '.join(config['question_types'])} ({question_num} problems)\n"
    
    for metric_name in config['metrics'].keys():
        if config['metrics'][metric_name] or metric_name == 'unit_test':
            numerator = sum([question_type_scores[metric_name]['numerator'] for question_type_scores in question_type_scores_list])
            denominator = sum([question_type_scores[metric_name]['denominator'] for question_type_scores in question_type_scores_list])
            try:
                normalized_numerator = numerator / denominator
                overall_scores_summary += f'{metric_name} score: {normalized_numerator:.3f}\n'
            except:
                overall_scores_summary += f'{metric_name} score: N/A\n'
    print(overall_scores_summary)
    os.makedirs(f'{config["output_dir"]}/', exist_ok=True)
    with open(f'{config["output_dir"]}/{config["model"]}_overall_scores_summary.txt', 'w') as f:
        f.write(overall_scores_summary)
        
def write_memory_problem(config, problem_key, file_key, content):
    """
    Save content into file_key of problem_key.
    """
    dirs = problem_key.split('_')
    output_dir = Path(config['memory_dir']) / config['exp'] / dirs[0] / dirs[1] / dirs[2]
    
    if file_key.startswith('context_'):
        file_path = file_key[len('context_'):]
        context_dir = file_path.split('/')[:-1]
        context_dir = ''.join([f'{d}/' for d in context_dir])
        file_name = file_path.split('/')[-1]
        os.makedirs(f'{output_dir}/', exist_ok=True)
        with open(f'{output_dir}/context_keys', 'a') as f:
            f.write(f'{file_key}\n')
    else:
        context_dir = ''
        file_name = file_key
    os.makedirs(f'{output_dir}/{context_dir}', exist_ok=True)
    with open(f'{output_dir}/{context_dir}{file_name}', 'w') as f:
        f.write(content)
        
def read_memory_problem(config, problem_key, file_key):
    """
    Read content from file_key of problem_key.
    """
    dirs = problem_key.split('_')
    output_dir = Path(config['memory_dir']) / config['exp'] / dirs[0] / dirs[1] / dirs[2]
    if file_key.startswith('context_'):
        file_path = file_key[len('context_'):]
        context_dir = file_path.split('/')[:-2]
        context_dir = '/'.join(context_dir)
        file_name = file_path.split('/')[-1]
        print(context_dir)
        print(file_name)
    else:
        context_dir = ''
        file_name = file_key
    if not os.path.exists(f'{output_dir}/{context_dir}/{file_name}'):
        return None
    with open(f'{output_dir}/{context_dir}/{file_name}', 'r') as f:
        content = f.read()
    return content

def write_memory(config, key, content):
    """
    Save content into key.
    """
    output_dir = Path(config['memory_dir']) / config['exp']
    # print(output_dir, key)
    os.makedirs(output_dir, exist_ok=True)
    with open(f'{output_dir}/{key}', 'w') as f:
        f.write(content)

def read_memory(config, key):
    """
    Read content from key.
    """
    output_dir = Path(config['memory_dir']) / config['exp']
    if not os.path.exists(f'{output_dir}/{key}'):
        return None
    with open(f'{output_dir}/{key}', 'r') as f:
        content = f.read()
    return content

def clean_memory(config):
    """
    Clean memory_dir.
    """
    output_dir = Path(config['memory_dir']) / config['exp']
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    