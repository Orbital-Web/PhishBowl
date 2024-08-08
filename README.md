# PhishBowl

## Introduction

This project is comprised of 2 parts: the **PhishBowl**, a phishing email dataset, and **PhishNet**, a phishing detection tool. Emails can be added to the PhishBowl via the API and PhishNet will automatically detect similar phishing scams in the future. You can analyze both email texts and screenshots of emails using PhishNet.

PhishNet uses an ensemble model comprised of a prompt-engineered GPT-4o and a modified weighted k-NN classifier to classify both common and new types of phishing scams. Essentially, the k-NN classifier allows the model to quickly learn and detect new types of scams, while the GPT-based model validates the k-NN classifier using its vast internal knowledge.

The k-NN classifier is modified in a way such that it can classify both positive and negative labels with only positive (phishing) labels in the PhishBowl. Thus, the classifier's false positive rate should not increase drastically as more and more phishing emails are added to the PhishBowl. Of course, the accuracy can be improved by also adding benign emails to the PhishBowl to help prevent false positives.

## Usage

1. Install [Docker](https://www.docker.com/products/docker-desktop/)
2. Add the following `.env` file inside `/api`:

   ``` sh
   env="prod"  # prod | stage | dev
   AZURE_OPENAI_API_KEY="YOUR_API_KEY"
   AZURE_OPENAI_ENDPOINT="YOUR_ENDPOINT"
   ```

3. Add an empty `.env` file inside `/app`
4. Compose up `docker-compose.yaml`

That's it! Go to [localhost:3000](localhost:3000) to use the interactive PhishNet webapp, or [localhost:8000](localhost:8000) to try out the API.

Note that for PhishNet to work, you'll need to add a few sample emails to the PhishBowl first. To see how you can populate Phishbowl using a dataset or evaluate different PhishNets, go to the [Advanced Usage](#advanced-usage) section.

## Development

1. Install [Docker](https://www.docker.com/products/docker-desktop/)
2. Add the following `.env` file inside `/api`:

   ``` sh
   env="dev"  # prod | stage | dev
   AZURE_OPENAI_API_KEY="YOUR_API_KEY"  # for GPTPhishNet and AzureDB
   AZURE_OPENAI_ENDPOINT="https://YOUR_ENDPOINT"  # for GPTPhishNet and AzureDB
   HUGGINGFACE_TOKEN_READ="hf_YOUR_HUGGINGFACE_READ_TOKEN"  # for HFBERTPhishNet
   HUGGINGFACE_TOKEN_WRITE="hf_YOUR_HUGGINGFACE_WRITE_TOKEN"  # for FineTunedBERTPhishNet
   ```

3. Add an empty `.env` file inside `/app`
4. To enable linting inside your preferred IDE, create a [Python virtual environment](https://docs.python.org/3/library/venv.html) and install the Python dependencies. Likewise, install the JavaScript dependencies for JS linting.

    ``` sh
    python -m venv venv
    source venv/bin/activate  # for unix
    ./venv/Scripts/activate  # for windows
    python -m pip install -r api/requirements.txt

    cd app
    npm install yarn
    yarn install
    ```

5. Compose up `docker-compose-dev.yaml` for a build with hot-reloading enabled on the webapp upon file changes

## Advanced Usage

There are several features available through `api/main.py` for things such as evaluating different PhishNets and populating the PhishBowl. To use it, ensure either `docker-compose.yaml` or `docker-compose-dev.yaml` is running, and either attach a shell to `api` or run the commands directly by appending them after `docker exec -it phishbowl-api-1`.

To get all available commands, run `python main.py -h`.

### Populating the PhishBowl

To analyze emails using PhishNet, you will need to add a few sample emails to the PhishBowl. You can either add your own emails via the API ([localhost:8000](localhost:8000)), or run `python main.py populate` to populate PhishBowl using a curated dataset, You will need to download the dataset yourself and add them to `/api/services/data/curated`. You will get a more detailed instruction when running populate for the first time.

For the first time you run populate after downloading the dataset, the data loader will load all emails in memory before shuffling them and splitting them into train and test sets and saving them to file. After this step, you may delete the `/api/services/data/curated` directory and future loading will happen lazily, thus not using as much memory.

### Evaluating PhishNets

There are several different PhishNets implemented already, such as GPTPhishNet, SemanticPhishNet, and FineTunedBERTPhishNET. Some of these PhishNets will require different API keys, as shown in the [Development](#development) section. You can evaluate different PhishNets by running `python main.py eval NAME`. There are other optional arguments such as a retrain flag or batch size which is important if your azure API is rate limited. For more details, run `python main.py eval -h`.
