import subprocess
import tempfile
import os
from pathlib import Path

def run_bash(bash_script, cwd=None):
    process = subprocess.Popen(['bash', '-c', bash_script], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8') + stderr.decode('utf-8')

def clean_dir(dir_path):
    entries = os.listdir(dir_path)
    for entry in entries:
        entry_path = os.path.join(dir_path, entry)
        if os.path.isfile(entry_path):
            os.remove(entry_path)
        else:
            clean_dir(entry_path)
            os.rmdir(entry_path)

def test(file_content, bash_script, problem_key, config):

    with tempfile.TemporaryDirectory() as temp_dir:
        # create labeled_code.yaml
        labeled_code_path = temp_dir + '/labeled_code.yaml'
        with open(labeled_code_path, 'w') as labeled_code:
            labeled_code.write(file_content)
        
        dirs = problem_key.split('_')
        output_dir = Path(config["memory_dir"]) / config['exp'] / dirs[0] / dirs[1] / dirs[2]
        if os.path.exists(output_dir / 'context_keys'):
            with open(output_dir / 'context_keys', 'r') as context_keys_file:
                context_keys = context_keys_file.read().splitlines()
            for context_key in context_keys:
                context_path = context_key[len(f'context_'):]
                context_tmp_path = temp_dir + '/' + context_path
                context_tmp_dir = os.path.dirname(context_tmp_path)
                with open(output_dir / context_path, 'r') as context_file:
                    context_file_content = context_file.read()
                if not os.path.exists(context_tmp_dir):
                    os.makedirs(context_tmp_dir)
                with open(context_tmp_path, 'w') as context_file:
                    context_file.write(context_file_content)

        # run the bash script in the tempdir
        target_out = run_bash(bash_script, temp_dir)
        
        run_bash('kubectl delete all --all', temp_dir)
    return 'cloudeval_unit_test_passed' in target_out, target_out