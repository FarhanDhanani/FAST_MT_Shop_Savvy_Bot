# A Neo4j-backed Chatbot using Python
## **FAST-MT TEAM SUBMISSION TO [SECURITY-AI-CHALLENGE](https://aichallenge.pk/)**
The repository contains our submission to the [SECURITY AI CHALLENGE](https://aichallenge.pk/).
[![N|Solid](https://upload.wikimedia.org/wikipedia/en/e/e4/National_University_of_Computer_and_Emerging_Sciences_logo.png)](https://nodesource.com/products/nsolid)

# SHOP SAVY BOT

A Neo4j-OpenAI-&-OLLAMA-backed Chatbot using Python/Streamlit

To run the application locally, you must setup following thigs
- CLIP Model (for video processing) 
- OLLAMA or OPEN AI account
- Neo4j Desktop Version
- secrets.toml file
- Config File

## SETUP CLIP Model

- download the "pytorch_model.bin" file from the following URL and place it inside ./models/ST-clip/0_CLIPModel/ directory
    - [clip-ViT-B-32 model from huggingface repository](https://huggingface.co/sentence-transformers/clip-ViT-B-32/tree/main/0_CLIPModel) 
        - Model size: 605MB, its a small model and can be run easily at local. I have tested it on 2017 MacBook Pro with following details
            - Processor: 3.1 GHz Quad-Core Intel Core i7
            - Graphics: Radeon Pro 555 2 GB Intel HD Graphics 630 1536 MB
            - Memory: 16 GB 2133 MHz LPDDR3

## Download and Setup OLLAMA
### Please note if you are willing to use OPEN AI key, and have paid account of OpenAI then you don't need to setup the OLLAMA
- Go to the OLLAMA [Download Page](https://ollama.com/)
- Download the setup file and install it on your machine
- After setuping the OLLAMA at your local run the following commands.

        1. ollama pull llama3
        2. ollama pull codegemma
        3. ollama pull mxbai-embed-large

## Download and Install Neo4j
 - Download Neo4j Desktop app from [HERE](https://neo4j.com/download/) and install it on your system
 - For details of installation instructions check the details present at the [official site](https://neo4j.com/docs/desktop-manual/current/installation/download-installation/)

### After installing Neo4j
After installation we need to setup the data
Open the Desktop application of Neo4j and follow the steps mentioned below.



    1. Create a new project by Clicking on the "new" icon and create project option.
![Alt text](images/neo4j/1.png)

    2. Rename the project name to My Project by howering on the project name clicking the edit icon and then pressing the tick icon.
![Alt text](images/neo4j/2.png)

    3. Add a Local DBMS to the project by clicking on the "Add" button and then selecting the "Local DBMS" option. After that enter the details name/password of your Local Database and select *5.19.0* Version number, as shown in the screenshots below. Please select the specified version only. Lastly click the create button.
    
![Alt text](images/neo4j/3.1.png) ![Alt text](images/neo4j/3.2.png)

    4. Click three dots besides the "Open" Button then click on the "Open Folder" option and then click on the "Import" button. A local directory location will be open open up, we need to paste (./neo4jScripts/products.json & ./neo4jScripts/categories.json) data files here. 
![Alt text](images/neo4j/4.1.png) ![Alt text](images/neo4j/4.2.png)

    5. Again click three dots besides the "Open" Button then click on the "Open Folder" option and then click on the "Configuration" option. A local directory location will be open open up, we need to paste (./neo4jScripts/apoc.conf) configuration files here. 
![Alt text](images/neo4j/5.png)

    6. Clink on the header row of the newly created DB ("neo4j 5.19.0" in our case) to open-up the details of the setuped local DBMS and then click on "Plugins" -> Click on APOC and then click on "install" button.
![Alt text](images/neo4j/6.png)

    7. Next Just click the "start" button, to start the Local DBMS.
![Alt text](images/neo4j/7.png)

    8. After that click the drop down button insied the "Open" Button on the top and select the "Neo4j Browser" option, as shown in the screen shot.
![Alt text](images/neo4j/8.png)

    9. In the newly opend window, shown in the screenshot below, we will going to execute the cypher statements.
![Alt text](images/neo4j/9.png)

    10. Open (./neo4jScripts/NEO-4J MIGRATION SCRIPTS LOCAL.md) file, and execute the cypher statements from SCRIPT-1 to SCRIPT-10, iteratively, one by one, as shown in the screenshot below.
![Alt text](images/neo4j/10.1.png) ![Alt text](images/neo4j/10.2.png)

## SETUP SECRETS.toml
    1. Create a secrets.toml file inside the (.streamlit) directory with the following contents
![Alt text](images/secretFile/secretsTomlFileContents.png)

To run the application, you must install the libraries listed in `requirements.txt`.
## SETUP CONFIG FILE TO CONTROL THE PROJECT EXECUTION
    1. Setup-Up Hyper Parameters:
        - MEMORY_MSG_BUFFER = 10 #It is the Number of messages to be kept saved at any given time to maintain the chat conversion.
        - N_VARIANTS_OF_MULTI_QUERY = 1 #It is the number of user query variants to be used while fetching answers through RAG.
        - MAX_TRIES_TO_CORRECT_JSON_STRING = 3 #It is the number retries to correct the json output that contains an array of multiple query variants in the form of strings.
        - MINIMUM_CUTOFF_THRESHOLD_FOR_SIMILARITY_SEARCH  :float = 0.0 #It is the minimum threshold of simillarity to fetch the document from graph database.
    2. Model Selection
        - USE_OPEN_AI_EMBEDDER = False #If it is set to true then open Embedder will be used. Otherwise ollama embedder will be used.
        - USE_OPEN_AI_CHAT_MODEL = False #If it is set to true then open Chat Model will be used. Otherwise ollama chat model will be used.
        - USE_OPEN_AI_WHISPER_MODEL = True #If it is set to true then open whisper model will be used. Otherwise, voice search feature will be disabled.
        
    3. Setup CLIP parameters to enable Video (from pintrest url) based search
        - VIDEO_CAPTURE_FRAME_RATE = 1000 #Frame rate to split the video into stream of images. 
        - FIND_K_RELEVANT_FRAMES_IN_VIDEO = 1 #Number of relevant frames that needs to be identified based on the given user query.
        - SAVE_VIDEO_WITH_NAME = "abc.mp4" #Name of file to save after downloading it from the given url.
        - SAVE_VIDEO_FILE_IN_FOLDER_NAME = "data" #Name of folder where splitted video frames will get saved. 
        - SAVE_VIDEO_FILE_ON_ROOT_PATH = "./"+SAVE_VIDEO_FILE_IN_FOLDER_NAME+"/" #Path where splitted video frames will get saved.
        - SAVE_FILE_NAME_WITH_HEAD = "frame"  #Head name with splitted video frames will get saved with prefix of number in sequence ordering.
        - ST_CLIP_MODEL_PATH = './models/ST-clip' #Path where CLIP model is saved.
        
![Alt text](images/configFile/configFile.png)

## RUN THE PROJECT
    1. First Create a virtual enviroment with the following command.
```sh
source myenv/bin/activate
```
    2. Ensure the virtual enviroment is activated and all the dependedncies are installed correctly with the following commands
```sh
pip3 install -r requirements.txt
```
    
    3. Lastly, make sure that neo4j database server is up and running then run the `streamlit run` command to start the app. 
```sh
streamlit run bot.py
```
