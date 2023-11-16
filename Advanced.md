# 🔧 Advanced Features

### Run Your Own Model 
* **Option 1: Replicate** \
You may benchmark your own model by deploying it on Replicate and include it in `config.json` as described [above](#replicate).
* **Option 2: Local** \
We are working on a local deployment option. Please stay tuned.

## Benchmark Configuration
A variety of advanced features are configurable in `config.json`.

#### Model Configuration
- **`models`**: Models to be benchmarked sequentially in one run.
- **`available_models`**: Models currently integrated into the benchmark.
- **`question_types`**: Dataset types to be benchmarked.
- **`available_question_types`**: Dataset types currently included in the benchmark.
  - *`original`*: Original dataset.
  - *`simplified`*: Augmented dataset - simplified questions.
  - *`translated`*: Augmented dataset - questions in Chinese.

#### Directory Settings
- **`source_dir`**: Source directory of the dataset.
- **`output_dir`**: Output directory where prompts, generated codes and scores will be saved.

#### Benchmark Settings
- **`save_as_cache`**: Save the intermediate results to `output_dir`.
- **`use_cache`**: Use the generated codes from `output_dir` for evaluation (if available).
- **`self_validation`**: Directly use reference yaml as input for scoring (used for validating the unit test environment).
- **`num_samples`**: Number of samples for each question.
- **`max_retry`**: Maximum retry if getting empty response from the model.
- **`max_eval_time_s`**: Maximum evaluation time per run (in case some unit tests do not return).

#### Metrics (`metrics`)
You may enable or disable each metric individually. The calculation is defined in [`metrics/`](metrics/). Please refer to our paper for a detailed description of each metric.


#### Multithreading (`ray`)
You may configure the number of threads for querying. Please pay attention to the rate limit of the model you are using. 4~16 are typically balanced numbers for most API-based models. Consider using a smaller number if you observe frequent warnings or empty responses.

#### Redis Configuration (`redis_local`)
You may configure the ip, port and db of your redis server if it is hosted elsewhere.

#### Prompt Engineering
- **`multishot`**: An example mutlishot prompting framework is integrated in [`prompt.py`](prompt.py).
- **`chain_of_thought`**: An example Chain-of-Thought framework is integrated in [`prompt.py`](prompt.py).

#### Problem Selection
- **`modes` / `available_modes`**: Selected / available modes to be included in the benchmark.
- **`libs` / `available_libs`**: Selected / available libraries to be included in the benchmark.
- **`problems_to_include` / `problems_to_exclude`**: Specific problems to be included / excluded in the benchmark, formatted as `<mode>_<lib>_<problem>` (e.g., `Kubernetes_pod_q1`).

## Setup Unit Test without using AWS AMI

#### Install Unit Test Prerequisites
(⚠️ Make sure to run as non-root user)
* Ubuntu

  * minikube and kubectl:
    (refered to https://minikube.sigs.k8s.io/docs/start/#:~:text=1,Installation)

    ```bash
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
    minikube version # should be 1.10 or later. Recommended: minikube version: v1.31.2
    ```

    ```bash
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    kubectl version --client
    #Client Version: v1.28.1
    #Kustomize Version: v5.0.4-0.20230601165947-6ce0bf390ce3
    #Server Version: v1.27.3
    ```
  * docker:
    (required by minikube, refered to https://docs.docker.com/desktop/install/linux-install/)

    ```bash
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    # run docker without root
    # https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user
    docker -v  # Docker version 24.0.2, build cb74dfc
    ```
  * Envoy:

    ```bash
    sudo apt update
    sudo apt install apt-transport-https gnupg2 curl lsb-release
    curl -sL 'https://deb.dl.getenvoy.io/public/gpg.8115BA8E629CC074.key' | sudo gpg --dearmor -o /usr/share/keyrings/getenvoy-keyring.gpg
    # Verify the keyring - this should yield "OK"
    echo a077cb587a1b622e03aa4bf2f3689de14658a9497a9af2c427bba5f4cc3c4723 /usr/share/keyrings/getenvoy-keyring.gpg | sha256sum --check
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/getenvoy-keyring.gpg] https://deb.dl.getenvoy.io/public/deb/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/getenvoy.list
    sudo apt update
    sudo apt install -y getenvoy-envoy
    sudo apt install -y jq
    sudo apt install openssl
    sudo apt install netcat
    ```
  * Istio:

    ```bash
    wget https://github.com/istio/istio/releases/download/1.18.2/istio-1.18.2-linux-amd64.tar.gz
    tar -zxvf istio-1.18.2-linux-amd64.tar.gz
    cd istio-1.18.2/
    export PATH=$PWD/bin:$PATH
    istioctl install --set profile=demo -y
    sudo rm ../istio-1.18.2-linux-amd64.tar.gz
    cd ..
    ```

* MacOS (only supporting Kubernetes for now, please disable others in ``config.json``)

  * minikube and kubectl:
    (refered to https://minikube.sigs.k8s.io/docs/start/#:~:text=1,Installation)

    ```bash
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
    sudo install minikube-darwin-amd64 /usr/local/bin/minikube
    ```
  * docker:
    (required by minikube, refered to https://docs.docker.com/desktop/install/mac-install/)

  * coreutils (need by ``timeout`` command in unit tests)

    ```bash
    brew install coreutils
    ```

#### Enable Unit Test in `config.json`
```json
"metrics": {
  "unit_test": true
}
```

#### Run the Benchmark
```bash
python benchmark.py
```
