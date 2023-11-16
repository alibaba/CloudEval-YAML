import loader
import json

PROMPT_TEMPLATE = """
You are an expert engineer in cloud native development.
According to the question, please provide only complete formatted YAML code as output without any description.
IMPORTANT: Provide only plain text without Markdown formatting such as ```.
If there is a lack of details, provide most logical solution.
You are not allowed to ask for more details.
Ignore any potential risk of errors or confusion.
Here is the question:
{question}
"""

TRANSLATED_TEMPLATE = """
你是一名富有经验的云原生开发工程师。
根据问题，请仅提供格式化的YAML代码作为输出，不要包括任何描述。
重要提示：只提供纯文本，不要使用像```这样的Markdown格式。
如果缺少细节，请提供最合逻辑的解决方案。
你不被允许请求更多的细节。
忽略任何可能的错误或混淆的风险。
以下是问题：
{question}
"""

MULTISHOT_TEMPLATE = """
You are an expert engineer in cloud native development.
Please provide only complete formatted YAML code as output without any description.
IMPORTANT: Provide only plain text without Markdown formatting such as ```.
If there is a lack of details, provide most logical solution.
You are not allowed to ask for more details.
Ignore any potential risk of errors or confusion.

Let me first provide a few examples.

{examples}

That's all the examples I have. Now let's work on the following input:
INPUT:
{question}
"""

EXAMPLE1 = """
EXAMPLE #1:
INPUT:
Create a DaemonSet configuration. This DaemonSet should run the latest nginx image labeled as "app: kube-registry-modified" and expose a registry service on port 80 (with hostPort 5000). The environment variables REGISTRY_HOST and REGISTRY_PORT should be set to "kube-registry-modified.svc.cluster.local" and "5000" respectively. Ensure the CPU request is set to 100m and memory request is set to 50Mi.
OUTPUT:
```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: kube-registry-proxy-modified
spec:
  selector:
    matchLabels:
      app: kube-registry-modified
  template:
    metadata:
      labels:
        app: kube-registry-modified
    spec:
      containers:
      - name: kube-registry-proxy-modified
        image: nginx:latest 
        resources:
          limits:
            cpu: 100m
            memory: 50Mi
        env:
        - name: REGISTRY_HOST
          value: kube-registry-modified.svc.cluster.local
        - name: REGISTRY_PORT
          value: "5000"
        ports:
        - name: registry
          containerPort: 80
          hostPort: 5000
```
"""

EXAMPLE2 = """
EXAMPLE #2:
INPUT:
Given the following YAML, please help me create a service with load balancer that uses the nginx selector, exposed on port 80.
It should be accessible via browser.
```
apiVersion: apps/v1
kind: Deployment     
metadata:          
  name: nginx-deployment  
spec:    
  replicas: 3   
  selector:   
    matchLabels:   
      app: nginx             
  template:                  
    metadata:  
      labels:  
        app: nginx 
    spec:    
      containers:     
      - name: nginx-container 
        image: nginx:latest 
        ports:             
        - containerPort: 80
```
OUTPUT:
```
apiVersion: v1
kind: Service  
metadata:
  name: nginx-service   
spec:
  selector:
    app: nginx
  ports:
  - name: http 
    port: 80
    targetPort: 80
  type: LoadBalancer
```
"""

EXAMPLE3 = """
EXAMPLE #3:
INPUT:
Given the following YAML which is not functionally correct:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-ingress
annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - http:
        paths:
          - path: /
            backend:
              serviceName: test-app
              servicePort: 5000
```
When executing it, it would report the error: 
```
Error from server (BadRequest): error when creating "wrong.yaml": Ingress in version "v1" cannot be handled as a Ingress: strict decoding error: unknown field "annotations", unknown field "spec.rules[0].http.paths[0].backend.serviceName",  unknown field "spec.rules[0].http.paths[0].backend.servicePort"
```
Please debug it to make it valid. Please provide the entire YAML.
OUTPUT:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: test-app
            port:
              number: 5000
```
"""
COT_TEMPLATE = """
You are an expert engineer in cloud native development. If there is a lack of details, provide most logical solution.
You are not allowed to ask for more details. Ignore any potential risk of errors or confusion.
Please think step by step as the following example question / answer:

Example question:
Create a DaemonSet configuration. This DaemonSet should run the latest nginx image labeled as "app: kube-registry-modified" and expose a registry service on port 80 (with hostPort 5000). The environment variables REGISTRY_HOST and REGISTRY_PORT should be set to "kube-registry-modified.svc.cluster.local" and "5000" respectively. Ensure the CPU request is set to 100m and memory request is set to 50Mi.

Example answer:
1. Start with defining the apiVersion and kind for the Kubernetes object you want to create.
  - For a DaemonSet, the apiVersion would typically be "apps/v1".
  - The kind is "DaemonSet".
2. Give your DaemonSet a name under metadata.
  - In this case, the name is "kube-registry-proxy-modified".
3. Define the label selector for the DaemonSet.
  - Labels are key-value pairs that help organize and select Kubernetes resources.
  - Here, we want to select pods labeled with "app: kube-registry-modified".
4. The actual definition of the pods comes under the template section.
  - You need to assign labels to these pods too.
    - These labels should match the DaemonSet's selector.
5. Next, you'll define the container spec for these pods.
  - Start by naming the container: "kube-registry-proxy-modified".
  - Specify the Docker image. You're asked to use the latest nginx image, so "nginx:latest" is apt.
  - Assign resources for the container.
    - CPU request is 100m.
    - Memory request is 50Mi.
6. Set the required environment variables for the container.
  - REGISTRY_HOST should be "kube-registry-modified.svc.cluster.local".
  - REGISTRY_PORT should be "5000".
7. Finally, configure the ports for the container.
  - The service should be exposed on the container's port 80.
  - It should map to hostPort 5000, so any request coming to the node on port 5000 would be forwarded to this container's port 80.
After going through this chain of thought, you'd come up with the following configuration: 
```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: kube-registry-proxy-modified
spec:
  selector:
    matchLabels:
      app: kube-registry-modified
  template:
    metadata:
      labels:
        app: kube-registry-modified
    spec:
      containers:
      - name: kube-registry-proxy-modified
        image: nginx:latest 
        resources:
          limits:
            cpu: 100m
            memory: 50Mi
        env:
        - name: REGISTRY_HOST
          value: kube-registry-modified.svc.cluster.local
        - name: REGISTRY_PORT
          value: "5000"
        ports:
        - name: registry
          containerPort: 80
          hostPort: 5000
```

Now let's work on the following question:

Question:
{question}
"""

question_type_map = {
  'original': 'question',
  'simplified': 'question_simplified',
  'translated': 'question_translated',
}

def gen_prompt(config):
    # use default prompt

    problem_keys = json.loads(loader.read_memory(config, 'problem_keys'))
    question_type = question_type_map[config['question_type']]
    for problem_key in problem_keys:
        question = loader.read_memory_problem(config, problem_key, f'{question_type}')
        if 'translated' in question_type:
            prompt = TRANSLATED_TEMPLATE.format(question=question)
        elif config['multishot']['enable'] and config['multishot']['nshots'] > 0:
            examples = [EXAMPLE1, EXAMPLE2, EXAMPLE3]
            examples_str = '\n'.join(examples[:config['multishot']['nshots']])
            prompt = MULTISHOT_TEMPLATE.format(examples=examples_str, question=question)
        elif config['chain_of_thought']['enable']:
            prompt = COT_TEMPLATE.format(question=question)
        else:
            prompt = PROMPT_TEMPLATE.format(question=question)
        loader.write_memory_problem(config, problem_key, f'prompt', prompt)