import replicate
import time
import threading

model = None
tokenizer = None
TIMEOUT = 900 # s

class RequestThread(threading.Thread):
    def __init__(self, prompt, model):
        threading.Thread.__init__(self)
        self.prompt = prompt
        self.model = model
        self.response = None

    def run(self):
        try:
            output = replicate.run(
                self.model,
                input={"prompt": self.prompt},
            )
            result = []
            for item in output: result.append(item)
            self.response = "".join(result)
        except Exception as e:
            print(type(e), e)

def get_resp_llama2_7b_chat(config, prompt):
    # thread = RequestThread(prompt, "meta/llama-2-7b-chat:8e6975e5ed6174911a6ff3d60540dfd4844201974602551e10e9e87ab143d81e")
    thread = RequestThread(prompt, "meta/llama-2-7b-chat:52551facc68363358effaacb0a52b5351843e2d3bf14f58aff5f0b82d756078c")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response
            
def get_resp_llama2_13b_chat(config, prompt):
    thread = RequestThread(prompt, "meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response
            
def get_resp_llama2_70b_chat(config, prompt):
    thread = RequestThread(prompt, "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response
            
def get_resp_llama_7b(config, prompt):
    thread = RequestThread(prompt, "replicate/llama-7b:ac808388e2e9d8ed35a5bf2eaa7d83f0ad53f9e3df31a42e4eb0a0c3249b3165")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response
            
def get_resp_llama_13b_lora(config, prompt):
    thread = RequestThread(prompt, "replicate/llama-13b-lora:4baede730d6bc13396e6dec0df5172bff658c014da9552bc17decfd6453d368c")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response
            
def get_resp_codellama_7b_instruct(config, prompt):
    thread = RequestThread(prompt, "meta/codellama-7b-instruct:534d3452e9398612a822f61145e287c298ebd8f3d05db8160f6be9dfcfcd5e4d")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response
            
def get_resp_codellama_13b_instruct(config, prompt):
    thread = RequestThread(prompt, "meta/codellama-13b-instruct:be553392065353425e0f0193d2a896d6a5ff201549f5d7cd9180c8dfdeac39ed")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response
            
def get_resp_codellama_34b_instruct(config, prompt):
    thread = RequestThread(prompt, "meta/codellama-34b-instruct:d12bd85bfbbaa88d4b8607aed1533951faeb62fe6c941a509ca68bdcbd0eb1e8")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response
            
def get_resp_qwen_7b_chat(config, prompt):
    thread = RequestThread(prompt, "niron1/qwen-7b-chat:d497d7da8c0be08ecc87e2f36133e35f8c8e67173f342ea6183143c24afa40b6")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response

def get_resp_codegen(config, prompt):
    thread = RequestThread(prompt, "andreasjansson/codegen:211bde4f1da227ce567f2db0fe3811d27435f69b3ac1c37237f3272fa1e79820")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response

def get_resp_codegen2_1b(config, prompt):
    thread = RequestThread(prompt, "lucataco/codegen2-1b:fb68fbc7e00ab75f8f0c3d860bf6ffd02ef0a857e90f8c91f6764a4ce803039a")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response

def get_resp_wizardcoder_15b_v1(config, prompt):
    thread = RequestThread(prompt, "lucataco/wizardcoder-15b-v1.0:b8c554180169aa3ea1c8b95dd6af4c24dd9e59dce55148c8f3654752aa641c87")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response

def get_resp_wizardcoder_34b_v1(config, prompt):
    thread = RequestThread(prompt, "rhamnett/wizardcoder-34b-v1.0:bae902bd8a4032fcf2295523b38da90aae7cc8ca2260e7ca9b8434a981d32278")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response

def get_resp_chatglm2_6b(config, prompt):
    thread = RequestThread(prompt, "nomagick/chatglm2-6b:215003d6f79761d1b2ac33633cf9da67a4559fe11bf18a744f6f7d874dca6270")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response

def get_resp_chatglm6b(config, prompt):
    thread = RequestThread(prompt, "tvytlx/chatglm6b:d552fb8df045d48f6c2284b905508446d0de5070d0521be0ce09e4f9ed462d99")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response

def get_resp_dolly_v2_12b(config, prompt):
    thread = RequestThread(prompt, "replicate/dolly-v2-12b:ef0e1aefc61f8e096ebe4db6b2bacc297daf2ef6899f0f7e001ec445893500e5")
    thread.start()
    thread.join(TIMEOUT)
    
    if thread.is_alive():
        print("Timeout")
        return ''
    
    return thread.response