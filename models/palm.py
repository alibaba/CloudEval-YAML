import time
import google.generativeai as palm
import os
palm.configure(api_key=os.getenv('PALM_API_KEY'))

# Check for supported models
# models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
# model = models[0].name
# print(model)

model = 'models/text-bison-001'

def get_resp(config, prompt):
    response = None
    while True:
        try:
            completion = palm.generate_text(
                model=model,
                prompt=prompt,
                temperature=0.75,
                # The maximum length of the response
                max_output_tokens=800,
            )
            response = completion.result
            if response == None: response = ""  # sometime response is None
            return response

        except Exception as e:
            print(type(e), e)
            time.sleep(10)