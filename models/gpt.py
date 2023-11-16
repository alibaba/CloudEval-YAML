import loader
import prompt
import json
import ray
import os
import openai
import time
from tqdm import tqdm

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def get_resp_gpt_3_5(config, prompt):
    response = None
    while response is None:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                api_key=OPENAI_API_KEY,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                request_timeout=60,
            )
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            print(type(e), e)
            # api is not stable, so we giveup retry
            return ''
            
def get_resp_gpt_4(config, prompt):
    response = None
    while response is None:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0314",
                api_key=OPENAI_API_KEY,
               messages=[
                    {"role": "user", "content": prompt},
                ],
                request_timeout=60,
            )
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            print(type(e), e)
            # api is not stable, so we giveup retry
            return ''
        
def get_resp_gpt_4_turbo(config, prompt):
    response = None
    while response is None:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                api_key=OPENAI_API_KEY,
               messages=[
                    {"role": "user", "content": prompt},
                ],
                request_timeout=60,
            )
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            print(type(e), e)
            # api is not stable, so we giveup retry
            return ''