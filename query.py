import loader
import prompt
import json
import ray
import os
import openai
import time
import re
from tqdm import tqdm
from models import gpt, replicate, palm

remote_models = {
    'gpt-3.5': gpt.get_resp_gpt_3_5,
    'gpt-4-turbo': gpt.get_resp_gpt_4_turbo,
    'gpt-4': gpt.get_resp_gpt_4,
    'palm-2': palm.get_resp,
    'llama-2-7b-chat': replicate.get_resp_llama2_7b_chat,
    'llama-2-13b-chat': replicate.get_resp_llama2_13b_chat,
    'llama-2-70b-chat': replicate.get_resp_llama2_70b_chat,
    'llama-7b': replicate.get_resp_llama_7b,
    'llama-13b-lora': replicate.get_resp_llama_13b_lora,
    'codellama-13b-instruct': replicate.get_resp_codellama_13b_instruct,
    'codellama-34b-instruct': replicate.get_resp_codellama_34b_instruct,
    'wizardcoder-15b-v1.0': replicate.get_resp_wizardcoder_15b_v1,
    'wizardcoder-34b-v1.0': replicate.get_resp_wizardcoder_34b_v1,
}

def get_results_as_available(ray_object_ids):
    remaining_ids = list(ray_object_ids)
    while remaining_ids:
        ready_ids, remaining_ids = ray.wait(remaining_ids)
        for obj_id in ready_ids:
            yield ray.get(obj_id)
            
def strip_generated_code(generated_code):
    # strip the line that contains "Here" and everything before
    generated_code = re.split(r'.*?\bHere\b.*?\n', generated_code)[-1]
    
    # extract the contents that wrapped in ...
    if '```' in generated_code:
        generated_code = generated_code.split('```')[1]
    if '<code>' in generated_code:
        generated_code = generated_code.split('<code>')[1]
    if 'START SOLUTION' in generated_code:
        generated_code = generated_code.split('START SOLUTION')[1]
    if '\\begin\{code\}' in generated_code:
        generated_code = generated_code.split('\\begin\{code\}')[1]
    generated_code = generated_code.split('\\end\{code\}')[0]
    generated_code = generated_code.split('END SOLUTION')[0]
    generated_code = generated_code.split('</code>')[0]
    generated_code = generated_code.strip()
    
    if 'apiVersion:' in generated_code:
        generated_code = 'apiVersion:' + generated_code.split('apiVersion:', maxsplit=1)[1]
    elif 'static_resources:' in generated_code:
        generated_code = 'static_resources:' + generated_code.split('static_resources:', maxsplit=1)[1]

    return generated_code

@ray.remote
def get_resp_from_remote_ray(config, query, get_resp_from_remote_func):
    result = {
        'problem_key': query['problem_key'],
        'sample_id': query['sample_id'],
        'generated_code': '',
    }
    retry = config['max_retry']
    while result['generated_code'] == '' and retry > 0:
        result['generated_code'] = get_resp_from_remote_func(config, query['prompt'])
        retry -= 1

    if result['generated_code'] is None:
        result['generated_code'] = ''
    loader.write_memory_problem(config, result['problem_key'], f"generated_code_{result['sample_id']}", strip_generated_code(result['generated_code']))
    if result['generated_code'] == '':
        print(f"Empty response for {result['problem_key']}_generated_code_{result['sample_id']}")
    return result

def get_resp_from_remote(config, get_resp_from_remote_func):

    problem_keys = json.loads(loader.read_memory(config, 'problem_keys'))

    if config['ray']['enable']:
        # remote query suitable for ray
        queries = []
        for problem_key in problem_keys:
            prompt = loader.read_memory_problem(config, problem_key, f'prompt')
            for sample_id in range(config['num_samples']):
                query = {
                    'problem_key': problem_key,
                    'sample_id': sample_id,
                    'prompt': prompt,
                }
                queries.append(query)

        ray.shutdown()
        ray.init(num_cpus=config['ray']['num_cpus'], ignore_reinit_error=True)
        ray_object_ids = [get_resp_from_remote_ray.remote(config, query, get_resp_from_remote_func) for query in queries]
        results = list(tqdm(get_results_as_available(ray_object_ids), total=len(queries), desc='Generating'))
    else:
        for problem_key in problem_keys:
            prompt = loader.read_memory_problem(config, problem_key, f'prompt')
            for sample_id in range(config['num_samples']):
                generated_code = get_resp_from_remote_func(config, prompt)
                loader.write_memory_problem(config, problem_key, f'generated_code_{sample_id}', strip_generated_code(generated_code))

def get_resp_from_local(config, get_resp_from_local_func, init_model_func):
    init_model_func(config)

    problem_keys = json.loads(loader.read_memory(config, 'problem_keys'))
    for problem_key in tqdm(problem_keys, desc='Generating'):
        prompt = loader.read_memory_problem(config, problem_key, f'prompt')
        generated_codes = get_resp_from_local_func(config, prompt)
        for sample_id, generated_code in enumerate(generated_codes):
            loader.write_memory_problem(config, problem_key, f'generated_code_{sample_id}', strip_generated_code(generated_code))

def get_resp(config):
    if config['model'] in remote_models:
        get_resp_from_remote(config, remote_models[config['model']])
    else:
        print(f"Model {config['model']} not supported")