"""Core library for IoT code generation and management.

This module provides core functionality for:
- Code generation and compilation for IoT devices
- Runtime execution and monitoring
- Code analysis and refinement
- Integration with various IoT operating systems (RIOT, Zephyr, Contiki)

The module uses LangChain for LLM interactions and supports multiple hardware platforms.
"""

import os
import threading
from typing import List, Tuple, Union, Dict, Optional

# Set environment variables that the OpenAI library expects
api_key = os.environ.get('OPENAI_API_KEY', '')
api_base = os.environ.get('OPENAI_API_BASE', '')

lock = threading.Lock()

import difflib
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import logging
import subprocess
import re
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import csv
from pydantic import BaseModel, Field
import re
import json
import serial
import time
import threading
from graphviz import Digraph
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import paramiko
import os
from enum import Enum
import sys


os.environ['OPENAI_API_KEY'] = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
os.environ['OPENAI_API_BASE'] = "https://xiaoai.plus/v1"
        
class LogLevel(Enum):
    """Enum for log levels with ANSI color codes."""
    INFO = '\033[92m'  # Green
    WARNING = '\033[93m'  # Yellow
    ERROR = '\033[91m'  # Red
    DEBUG = '\033[94m'  # Blue
    STEP = '\033[95m'  # Purple
    RESET = '\033[0m'  # Reset color

class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to log levels."""
    
    def format(self, record):
        if not hasattr(record, 'color'):
            record.color = LogLevel[record.levelname].value if record.levelname in LogLevel.__members__ else ''
        if not hasattr(record, 'reset'):
            record.reset = LogLevel.RESET.value
        return super().format(record)

# Configure logging
logger = logging.getLogger('IoTCodeGen')
logger.setLevel(logging.INFO)

# Console handler with color formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
colored_formatter = ColoredFormatter(
    '%(asctime)s %(color)s[%(levelname)s]%(reset)s [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(colored_formatter)

# File handler for persistent logging
file_handler = logging.FileHandler('iot_codegen.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

STEP_LEVEL = 25
logging.addLevelName(STEP_LEVEL, 'STEP')

def step(self, message, *args, **kwargs):
    """Custom log level for major processing steps."""
    if self.isEnabledFor(STEP_LEVEL):
        self._log(STEP_LEVEL, message, args, **kwargs)

logging.Logger.step = step

# Code State
class CodeState:
    """Represents the current state of code generation and execution.
    
    Attributes:
        error (str): Error message if any
        errorstate (str): Current error state ("pass" or "not pass")
        messages (List[Tuple[str, str]]): List of message tuples (role, content)
        generation (str): Generated code content
        runtimelogs (str): Runtime execution logs
        runtimestate (str): Current runtime state
        iterations (int): Number of generation iterations
    """
    
    def __init__(
        self,
        error: str = "",
        errorstate: str = "",
        messages: Optional[List[Tuple[str, str]]] = None,
        generation: str = "",
        runtimelogs: str = "",
        runtimestate: str = "",
        iterations: int = 0
    ):
        self.error = error
        self.errorstate = errorstate
        self.messages = messages if messages is not None else []
        self.generation = generation
        self.runtimelogs = runtimelogs
        self.runtimestate = runtimestate
        self.iterations = iterations

    def print_state(self) -> None:
        """Print the current state information."""
        print(f"Error: {self.error}")
        print(f"Error State: {self.errorstate}")
        print(f"Messages: {self.messages}")
        print(f"Generation: {self.generation}")
        print(f"Iterations: {self.iterations}")

    def to_json(self, i: int, count: int, program_name: str, process_id: int, method_type: str) -> None:
        """Save the current state to a JSON file.
        
        Args:
            i: Current iteration number
            count: Total count
            program_name: Name of the program
            process_id: Process identifier
            method_type: Type of method being used
        """
        data = {
            "error": self.error,
            "errorstate": self.errorstate,
            "messages": self.messages,
            "generation": self.generation,
            "runtimelogs": self.runtimelogs,
            "runtimestate": self.runtimestate,
            "iterations": self.iterations
        }
        output_path = f"../output/{program_name}/{process_id}/{method_type}/{count}_state.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

# Data model
class Code(BaseModel):
    """Schema for code solutions to questions."""
    prefix: str = Field(description="Description of the problem and approach")
    block: str = Field(description="Complete code")
    
class Ans(BaseModel):
    """Schema for code solutions to questions."""
    answer: str = Field(description="Answer to the question")

class CodeDeepseek(BaseModel):
    """Schema for Deepseek code solutions."""
    block: str = Field(description="Complete code")

class ContextCode(BaseModel):
    """Schema for code context information."""
    imports: List[str] = Field(description="Imported header files")
    apis: List[str] = Field(description="Function names of APIs")

class GraphCode(BaseModel):
    """Schema for code relationship graphs."""
    relationship: List[List[Union[str, float]]] = Field(
        description="Relationships between headers and APIs"
    )

class ExplainCode(BaseModel):
    """Schema for code explanations."""
    explain: List[str] = Field(description="Explanations of headers or APIs")

class FSMCode(BaseModel):
    """Schema for Finite State Machine representations."""
    FSMs: str = Field(description="FSMs in JSON format")

class AnalysisCode(BaseModel):
    """Schema for code analysis reports."""
    report: str = Field(description="Error analysis report")

class OutlineCode(BaseModel):
    """Schema for code outlines."""
    outline: List[str] = Field(description="Code outline")

class InjectedCode(BaseModel):
    """Schema for code with injected logs."""
    block: str = Field(description="Complete code with injected logs")

class QuestionType(BaseModel):
    """Schema for question type classification."""
    type: str = Field(description="Yes or No")

class ExplainHeadersAPIs(BaseModel):
    """Schema for API/header explanations."""
    explaination: str = Field(description="Explanation of headers or APIs")
    
class RemoveHeaderAPIs(BaseModel):
    """Schema for removing header APIs."""
    block: str = Field(description="Complete code with removed irrelevant headers")

def remove_ansi_escape_sequences(text: str) -> str:
    """Remove ANSI escape sequences from text.
    
    Args:
        text: Input text containing ANSI escape sequences
        
    Returns:
        Text with ANSI escape sequences removed
    """
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
    return ansi_escape.sub('', text)

def rag(data_file: str) -> Dict[str, str]:
    """Load and process data from a CSV file for retrieval-augmented generation.
    
    Args:
        data_file: Path to the CSV file containing code data
        
    Returns:
        Dictionary mapping IDs to code snippets
    """
    data_dict = {}
    try:
        with open(data_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    id = row['id']
                    code = row['code']
                    data_dict[id] = code
                except Exception as e:
                    logging.error(f"An error occurred while processing the row: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    return data_dict

def search_topk_cos(
    ragdata: Dict[str, str],
    question: str
) -> List[str]:
    """Search for top-k most similar items using cosine similarity.
    
    Args:
        ragdata: Dictionary of reference data
        question: Query text to compare against
        
    Returns:
        List of most similar items
    """
    data = pd.DataFrame(list(ragdata.items()), columns=['id', 'item'])
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(data['item'].tolist() + [question])
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
    data['similarity'] = similarities
    data_sorted = data.sort_values(by='similarity', ascending=False)
    cutoff_index = int(len(data_sorted) * 0.01)
    top_items = data_sorted.head(cutoff_index)
    
    for _, row in top_items.iterrows():
        logging.info(f"Item ID: {row['item']}, Similarity Score: {row['similarity']}")
    
    return top_items['item'].tolist()

def search_topk_difflib(
    ragdata: Dict[str, str],
    question: str,
    generation: str,
    rate: float
) -> List[str]:
    """Search for top-k most similar items using difflib sequence matcher.
    
    Args:
        ragdata: Dictionary of reference data
        question: Query text
        generation: Generated code text
        rate: Cutoff rate for similarity matching
        
    Returns:
        List of most similar items
    """
    def compute_similarity(code1: str, code2: str) -> float:
        return difflib.SequenceMatcher(None, code1, code2).ratio()
    
    data = pd.DataFrame(list(ragdata.items()), columns=['id', 'item'])
    content = str(question) + str(generation)
    data['similarity'] = data['item'].apply(lambda x: compute_similarity(x, content))
    data_sorted = data.sort_values(by='similarity', ascending=False)
    cutoff_index = int(len(data_sorted) * rate)
    top_items = data_sorted.head(cutoff_index)
   
    return top_items['item'].tolist()

def create_vectorstore() -> Chroma:
    """Create and initialize a vector store for semantic search.
    
    Returns:
        Initialized Chroma vector store
    """
    logging.info("Starting vector store creation")
    loader = TextLoader("../datasets/api.csv")
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(data)
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)
    logging.info("Vector store creation completed")
    return vectorstore

def create_fsms() -> List[Dict]:
    """Create FSM (Finite State Machine) representations from JSON files.
    
    Returns:
        List of FSM dictionaries loaded from JSON files
    """
    fsms_json = []
    for root, _, files in os.walk("../fsms"):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        fsms_json.append(data)
                except (json.JSONDecodeError, IOError) as e:
                    logging.error(f"Error reading {file_path}: {e}")
    return fsms_json

def outline_chain(code_model):
    code_model = "gpt-4o"
    # Outline prompt
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1"
    outline_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a coding assistant with expertise in RIOT. \n  
                    Develop a well-structured solution for the provided problem that obeys the constraints and 
                    passes the example test cases. Ensure modularity and considering potential edge cases and failures. 
                    Start by outlining the required code modules, including function headers and signatures. 
                    Subsequently, proceed to implement each module to create the final code.
                    In simpler terms, create a clean and organized solution for the given problem. Break it down into smaller 
                    parts (modules) with clear function names. Once the structure is ready, write the actual code for each module to complete the solution.
                    Please write your modules answer using ```module.
                    Note, each moudule contains a function. The total number of modules is limited to two or fewer.
                    For example:
                    ```module
                    void *thread1_function(void *arg) {{
                        (void)arg;
                        while (1) {{
                            printf("hello_world thread2\n");
                            xtimer_sleep(1);
                        }}
                        return NULL;
                    }}
                    ```

                    ```module
                    void *thread2_function(void *arg) {{
                        (void)arg;
                        while (1) {{
                            printf("hello_world thread1\n");
                            xtimer_sleep(1);
                        }}
                        return NULL;
                    }}
                    ```
                """
            ),
            ("placeholder", "{problem}"),


        ]
    )
    expt_llm = code_model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    outline_chain_oai = outline_prompt | llm.with_structured_output(OutlineCode)
    return outline_chain_oai

def chat_chain(model):
    model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1"
    # Code_gen prompt
    gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a coding assistant with expertise in embedded system. \n 
                You should answer the user question: {question}.
                """,
            )
        ]
    )
    expt_llm = model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    gen_chain_oai = gen_prompt | llm.with_structured_output(Ans)

    return gen_chain_oai

def openaichain(code_model):

    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1"
    # Code_gen prompt
    code_gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a coding assistant with expertise in RIOT. \n 
                Here is a full set of RIOT documentation:  \n ------- \n  {context} \n ------- \n You should adopt CoT and answer the user 
                question based on the above provided documentation step by step.\n
                You must contain main function (int main()). \n
                Ensure any code you provide can be executed \n 
                Your code must not use placehoder code and simulate code, which need user to complete. \n
                with all required imports and variables defined. Structure your answer with a description of the code solution. \n
                Then list the imports. And finally list the functioning code block. Here is the user question:
                You must include header files in descending alphabetical order by their first letter.
                You cannot use "ESP_IF_WIFI_STA" and "IPV4".
                """,
                    ),
                ("placeholder", "{messages}"),
        ]
    )
    expt_llm = code_model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    code_gen_chain_oai = code_gen_prompt | llm.with_structured_output(Code)

    return code_gen_chain_oai

def deepseekchain(code_model):

    # deepseek
    # api_key = 'sk-c7db17eef21346f4a4a94e450c759a63'
    # api_base ='https://api.deepseek.com/v1'

    code_model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1"

    # Code_gen prompt
    code_gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a coding assistant with expertise in RIOT. \n 
                Here is a full set of RIOT documentation:  \n ------- \n  {context} \n ------- \n You should adopt CoT and answer the user 
                question based on the above provided documentation step by step.\n
                You must contain main function (int main()). \n
                Ensure any code you provide can be executed \n 
                Your code must not use placehoder code and simulate code, which need user to complete. \n
                You cannot use "ESP_IF_WIFI_STA" and "IPV6".
                Your answer must wrap with "```c".
                Here is the user question:
                """,
                    ),
                ("placeholder", "{messages}"),
        ]
    )

    expt_llm = code_model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    code_gen_chain_oai = code_gen_prompt | llm

    return code_gen_chain_oai

def code_refine_chain(code_model):
    code_model = "gpt-4o"
    # Code_gen prompt
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1"
    code_refine_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a coding assistant with expertise in RIOT. \n 
                Here is the provided relevant FSMs:  \n ------- \n  {FSMs} \n ------- \n
                Here is the code and the execution logs: \n ------- \n  {code} \n ------- \n
                \n ------- \n  {logs} \n ------- \n
                You need to analyze the program's execution logs to identify the causes of code errors, and 
                then modify the code logic without altering any APIs or header files to ensure that the code fully complies 
                with the state transitions involved in the FSMs (Finite State Machines) for correct operation.
                You must not implement the code in the form of mutiple state transitions.
                Finally, structure your answer with a description of the code solution.
                """
            )
        ]
    )
    expt_llm = code_model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    code_refine_chain_oai = code_refine_prompt | llm.with_structured_output(Code)

    return code_refine_chain_oai

def context_aware_chain(code_model):
    
    code_model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1"
    # create context prompt
    code_gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a coding assistant with expertise in RIOT. \n  
                Here is the generated code: \n ------- \n  {code} \n ------- \n 
                You first should extract all the imported header files and apis from the generated code. \n 
                Here is the problem: \n ------- \n  {problem} \n ------- \n 
                Here is the docs: \n ------- \n  {docs} \n ------- \n 
                Then, based on the extracted header files and APIs, you must find more relevent header files and APIs accroding provided problem and docs.
                The header file only contain the header name. \n
                The apis must only contain the function name.
                So, you should list all the extracted imported header files and APIs from the generated code and the relevant 
                header files and APIs you found from the above problem and docs.
                
                """
            )
        ]
    )
    expt_llm = code_model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    context_chain_oai = code_gen_prompt | llm.with_structured_output(ContextCode)

    return context_chain_oai

def graph_create_chain(code_model):

    code_model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1"
    # create context prompt
    code_gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a coding assistant with expertise in RIOT. \n  
                Our question is  \n ------- \n  {question} \n ------- \n.
                You must provide a correlation score for the each pair apis or headers
                in the list \n ------- \n  {list} \n ------- \n.
                It includes their reverse order, to ensure at least 100 relationships
                The correlation score should be represented by weighted values ranging from 0 to 100 . 
                Your output format must follow by
                For example:
                ("question", "MQTTClient.h":  86)
                ("MQTTClient.h", "esp_wifi.h": 23)
                ("MQTTClient.h", "MQTTPublish": 76)
                """
            )
        ]
    )
    expt_llm = code_model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    graph_chain_oai = code_gen_prompt | llm.with_structured_output(GraphCode)

    return graph_chain_oai

def explain_create_chain(code_model):

    code_model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1" 
    # create context prompt
    code_gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a coding assistant with expertise in RIOT. \n  
                You need to provide a detailed explanation for the each api or header in the list \n ------- \n  {list} \n ------- \n., 
                including its purpose and usage process. Please strictly output it as a single paragraph.
                
                """
            )
        ]
    )
    expt_llm = code_model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    explain_chain_oai = code_gen_prompt | llm.with_structured_output(ExplainCode)

    return explain_chain_oai

def execution_aware_chain(code_model):

    code_model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1" 
    # FSM_gen prompt
    fsm_gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                """You are a coding assistant with expertise in code programming. \n  
                As a professional IoT programmer proficient in Finite-state machines (FSM), 
                you are tasked with meticulously analyzing the given IoT program to construct comprehensive FSMs. 
                Specifically, you need to:
                Firstly, identify and extract all the states present in the program.
                Then, extract the transition relationships between these states along with the conditions that govern these transitions.
                The FSMs you generate must cover as many states and state transitions as possible.
                The FSMs must contain appropriate exception handling logic, such as reconnecting in the event of network connection failures.
                Output the constructed FSM in JSON format.
                For example:
                your output need follow the below JSON format:
                {{
                    "states": [
                        {{
                            "name": "INIT",
                            "transitions": [
                                {{
                                    "condition": "DHT_INIT_OK",
                                    "target": "NETWORK_INIT"
                                }},
                                {{
                                    "condition": "DHT_INIT_FAIL",
                                    "target": "ERROR"
                                }}
                            ]
                        }},
                        {{
                            "name": "NETWORK_INIT",
                            "transitions": [
                                {{
                                    "condition": "NETWORK_INIT_OK",
                                    "target": "MQTT_INIT"
                                }},
                                {{
                                    "condition": "NETWORK_INIT_FAIL",
                                    "target": "NETWORK_RECONNECT"
                                }}
                            ]
                        }},
                    ]
                }}
                """
            ),
            ("placeholder", "{program}"),
        ]
    )
    expt_llm = code_model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    fsm_chain_oai = fsm_gen_prompt | llm.with_structured_output(FSMCode)

    return fsm_chain_oai

def execution_analysis_chain(code_model):

    code_model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1" 
    # create context prompt
    code_analysis_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a coding assistant with expertise in RIOT and FSMs. \n  
                Here is the curr_code and the corresponding curr_FSMs:  
                \n ------- \n  {curr_code} \n ------- \n 
                \n ------- \n  {curr_FSMs} \n ------- \n 
                There may be logical errors in this code, such as a lack of robustness in some logic. 
                You need to identify the issues in the code based on the provided ref_FSMs fragments and suggest corrective measures.
                Here is the ref_FSMs:  
                \n ------- \n  {ref_FSMs} \n ------- \n 
                Specifically, you need first extract the pattern 
                (e.g. Network connected fail -> Network reconnected -> network connected successfully -> mqtt connected) in the both curr_FSMs and ref_FSMs. 
                Then, you need to analyze the difference between the pattern of curr_FSMs and ref_FSMs.
                Finally, you must report the incorrect matching patterns in the curr_code and provide corrective measures.
                """
            )
        ]
    )
    expt_llm = code_model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    analysis_chain_oai = code_analysis_prompt | llm.with_structured_output(AnalysisCode)

    return analysis_chain_oai

def execution_inject_chain(code_model):

    code_model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1" 
    # create context prompt
    code_inject_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a coding assistant with expertise in RIOT. \n  
                Here is the relevant FSMs:  \n ------- \n  {FSMs} \n ------- \n 
                Based on the reference FSMs provided above, 
                please add logging statements at key points in the following code to capture as many runtime characteristics as 
                possible in order to trace the correctness of the program during execution.
                Here is the code:  \n ------- \n  {Code} \n ------- \n 
                You are absolutely not allowed to modify the code structure, code APIs, header files, or any other parts, except for adding or removing logs.
                Finally, structure your answer with sufficient logging.
                """
            )
        ]
    )
    expt_llm = code_model
    llm = ChatOpenAI(temperature=0, model=expt_llm, openai_api_key= api_key, 
    openai_api_base= api_base)
    inject_chain_oai = code_inject_prompt | llm.with_structured_output(InjectedCode)

    return inject_chain_oai

def code_task_chain(code_model):

    code_model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1"   

    """Determine if a given question is a coding task."""
    coding_task_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert assistant in identifying coding tasks. 
                Please analyze the following question and determine if it is a coding-related task. 
                Simply respond with 'Yes' if it is a coding task and 'No' otherwise.
                Here is the question:  \n ------- \n  {question} \n ------- \n 
                """
            )
        ]
    )
    llm = ChatOpenAI(temperature=0, model=code_model, openai_api_key=api_key, openai_api_base=api_base)
    codetask_chain = coding_task_prompt | llm.with_structured_output(QuestionType)
    return codetask_chain

def remove_header_apis_chain(code_model):
    code_model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1"
    coding_task_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert assistant in coding. 
                Here is the question:  \n ------- \n  {question} \n ------- \n 
                Here is the code:  \n ------- \n  {code} \n ------- \n 
                You need to remove the headers from the code that are not relevant to the question/code or are outliers.
                You must not remove any header files that are required by the code.
                You must not modify the code except for removing the headers.
                """
            )
        ]
    )
    code_model = "gpt-4o"
    llm = ChatOpenAI(temperature=0, model=code_model, openai_api_key=api_key, openai_api_base=api_base)
    remove_header_apis_chain = coding_task_prompt | llm.with_structured_output(RemoveHeaderAPIs)
    return remove_header_apis_chain

def api_header_extend_chain(code_model):
    code_model = "gpt-4o"
    api_key = "sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo"
    api_base = "https://xiaoai.plus/v1"
    coding_task_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert assistant in coding. 
                Please provide a professional explanation for the following headers or APIs, limited to 20 words.
                Here is the headers or APIs:  \n ------- \n  {question} \n ------- \n 
                """
            )
        ]
    )
    code_model = "gpt-4o"
    llm = ChatOpenAI(temperature=0, model=code_model, openai_api_key=api_key, openai_api_base=api_base)
    headers_apis_chain = coding_task_prompt | llm.with_structured_output(ExplainHeadersAPIs)
    return headers_apis_chain

def fsm_generate(model, program_path, full_code, program_name):

    def visualize_fsm(json_file, output_name):
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                fsm_data = json.load(file)
        except FileNotFoundError:
            logging.error(f"The file {json_file} does not exist.")
            return
        except IOError:
            logging.error(f"An error occurred while reading the file {json_file}.")
            return
        dot = Digraph(comment='FSM')
        states = fsm_data.get('states', [])
        for state in states:
            state_name = state.get('name')
            dot.node(state_name, state_name)
            transitions = state.get('transitions', [])
            for transition in transitions:
                condition = transition.get('condition', '')
                target = transition.get('target', '')
                dot.edge(state_name, target, label=condition)

        dot_file_path = 'fsms/' + output_name + '.dot'
        png_file_path = 'fsms/' + output_name + '.png'
        dot.save(dot_file_path)
        dot.render(png_file_path, format='png', cleanup=True)
        logging.info(f"FSM visualization saved as {png_file_path}")

    program = []
    if program_path != None and full_code == None:
        try:
            with open(program_path, 'r', encoding='utf-8') as file:
                program.append(file.read())
        except FileNotFoundError:
            logging.error(f"The file {program_path} does not exist.")
            return
        except IOError:
            logging.error(f"An error occurred while reading the file {program_path}.")
            return
    elif program_path == None and full_code != None:
        program.append(full_code)

    fsm_chain_oai = execution_aware_chain(model)
    fsm_solution = fsm_chain_oai.invoke(
        {"program": program}
    )
    
    output_file_path = '../fsms/fsms/' + program_name + '_fsm.json'
    try:
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(fsm_solution.FSMs)
        logging.info(f"Result written to {output_file_path}")
    except IOError:
        logging.error(f"An error occurred while writing to the file {output_file_path}.")
        return
    visualize_fsm(output_file_path, program_name + '_fsm')

    return fsm_solution.FSMs
    

def fsms_extract(file_path):

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("The file was not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")

def graphinfer(contextgraph):

    def check_graph_solution_format(graph_solution):
        for item in graph_solution:
            if not isinstance(item, list) or len(item) != 3:
                return False
            header1, header2, weight = item
            if not (isinstance(header1, str) and isinstance(header2, str) and isinstance(weight, float)):
                return False
        return True

    if not check_graph_solution_format(contextgraph):
        print("The format of graph_solution is incorrect.")
        return " ", " "
    limit = 3
    G = nx.Graph()
    for item in contextgraph:
        header1, header2, weight = item
        if len(header1) > 50: header1 = 'question'
        if len(header2) > 50: header2 = 'question'
        if weight >= limit:
            G.add_edge(header1, header2, weight=weight)

    # plt.figure(figsize=(20, 16))  
    # pos = nx.spring_layout(G, k=2)  
    # edges = G.edges(data=True)
    # edge_labels = {(u, v): d['weight'] for u, v, d in edges}

    # nx.draw_networkx_nodes(G, pos, node_size=700)
    # nx.draw_networkx_edges(G, pos, edgelist=edges)
    # nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    # plt.savefig("../output/graph.png")

    graph = {}
    for connection in contextgraph:
        node1, node2, value = connection
        if len(node1) > 50: node1 = 'question'
        if len(node2) > 50: node2 = 'question'
        if value >= limit:
            if node1 not in graph:
                graph[node1] = []
            if node2 not in graph:
                graph[node2] = []
            graph[node1].append(node2)
            graph[node2].append(node1)

    def dfs(node, visited):
        if node not in visited:
            visited.add(node)
            for neighbor in graph.get(node, []):
                dfs(neighbor, visited)

    visited = set()
    dfs('question', visited)
    correct_header_api = [node for node in visited]
    correct_headers = [item for item in correct_header_api if item.endswith('.h')]
    correct_apis = [item for item in correct_header_api if not item.endswith('.h')]

    return correct_headers, correct_apis

def substring_similarity(s1, s2):
    
    
    # apis_headers_chain_oai = api_header_extend_chain("gpt-4o")
    # apis_headers_solution = apis_headers_chain_oai.invoke(
    #       {"question": str(s1)}
    #     )
    # s1 = apis_headers_solution.explaination
    
    # apis_headers_solution = apis_headers_chain_oai.invoke(
    #       {"question": str(s2)}
    #     )
    # s2 = apis_headers_solution.explaination
    
    # print(s1, s2)
    
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_length = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_length:
                    max_length = dp[i][j]
            else:
                dp[i][j] = 0

    return max_length

def substring_similarity_rate(s1, s2):
    
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_length = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_length:
                    max_length = dp[i][j]
            else:
                dp[i][j] = 0

    total_length = m + n
    ratio = max_length / total_length if total_length > 0 else 0

    return ratio

def outline(
    model: str,
    question: str
) -> List[str]:
    """Generate code outline based on the question.
    
    Args:
        model: Name of the language model to use
        question: Input question to generate outline for
        
    Returns:
        List of outline items
    """
    problem = [question]
    outline_chain_oai = outline_chain(model)
    outline_solution = outline_chain_oai.invoke(
        {"problem": problem}
    )
    return outline_solution.outline

def intergration_gen(process_id, program_name, model, state, question, sub_solutions, iscontext, role):

    messages = state.messages
    iterations = state.iterations
    errorstate = state.errorstate
    error = state.error
    messages += [
      (
        "user",
        f"{question}"
      )
    ]

    if errorstate == "not pass":
        
        messages += [
            (
                "user",
                f"Now, try again. Check the error information: {error} and Invoke the code tool to structure the output with a prefix and code block:",
            )
        ]
    
    concatenated_content = ''.join(sub_solutions)
    code_gen_chain_oai = openaichain(model)
    intergration_solution = code_gen_chain_oai.invoke(
        {"context": concatenated_content, "messages": messages}
    )

    state.generation = intergration_solution.block
    state.iterations += 1

    if iscontext:

        context_chain_oai = context_aware_chain(model)
        context_solution = context_chain_oai.invoke(
        {"code": intergration_solution.block, "docs": concatenated_content, "problem": question}
        )
        whitelist = []
        blacklist = []

        for header in context_solution.imports:
            if str(header) in str(concatenated_content):
                whitelist.append(header)
            else:
                blacklist.append(header)

        for api in context_solution.apis:
            if str(api) in str(concatenated_content):
                whitelist.append(api)
            else:
                blacklist.append(api)

        messages += [
            (
                "assistant",
                f"whitelist (you must use them in your answer code!): {str(whitelist)}"
            )
        ]
        messages += [
            (
                "assistant",
                f"blacklist (you must not use them in your answer code!): {str(blacklist)}"
            )
        ]

    file_path = '../output/'+program_name+'/'+str(process_id)+'/'+program_name+'_'+str(role)+'_'+str(state.iterations)+'_solution.c'

    with open(file_path, 'w') as file:
        file.write(state.generation)

def code_gen(process_id, model, state, vectorstore, question, iscontext, isexecution, isuserreq, usereq, 
             whitelist, blacklist, correct_header_apis, program_name, role, method_type, device_type, os_type):

    state.messages = []
    messages = state.messages
    iterations = state.iterations
    errorstate = state.errorstate
    error = state.error
    correct_apis = []
    correct_headers = []
    logger.info(f"[{program_name}] Starting code generation iteration {iterations}")
    logger.info(f"[{program_name}] Using model: {model}")

    messages += [
      (
        "user",
        f"{question}"
      )
    ]

    if errorstate == "not pass":
        messages += [
        (
            "user",
            f"Now, try again. Check the error information: {error} and Invoke the code tool to solve the error and structure the output with a prefix and code block. "
        )
        ]
        if program_name == "RIOT_MQTT":
           messages += [
        (
            "user",
            "Note: you must ensure that 'MQTTClient.h' is the last header file to be included, if it needs to be used."
        )
        ]
        if os_type == "FreeRTOS":
            messages += [
            (
                "user",
                "Note: you must ensure that 'freertos/task.h' is the last header file to be included, if it needs to be used."
            )
        ]
        
    
    # RAG: imports 
    rate_imports = 1
    if os_type == "RIOT":
        print("RIOT Docs")
        ragimports = rag("../datasets/imports_riot.csv")
        ragapis = rag("../datasets/api_riot.csv")
    elif os_type == "Zephyr":
        print("Zephyr Docs")
        ragimports = rag("../datasets/imports_zephyr.csv")
        ragapis = rag("../datasets/api_zephyr.csv")
    elif os_type == "Contiki":
        print("Contiki Docs")
        ragimports = rag("../datasets/imports_contiki.csv")
        ragapis = rag("../datasets/api_contiki.csv")
    elif os_type == "FreeRTOS":
        print("FreeRTOS Docs")
        ragimports = rag("../datasets/imports_freertos.csv")
        ragapis = rag("../datasets/api_freertos.csv")

    selectedimpots = search_topk_difflib(ragimports, question, state.generation, rate_imports)
    # RAG: apis
    rate_apis = 0.25
    selectedapis = search_topk_difflib(ragapis, question, state.generation, rate_apis)
    concatenated_content = "import:"+ str(selectedimpots) + "apis:"+str(selectedapis)

    if isexecution and iterations > 0:
        # execution-aware
        logger.info("Start FSMs analysis")
        # search similar FSMs
        similarities_fsms = []
        FSMS_json = create_fsms()
        for FSM in FSMS_json:
            sim = difflib.SequenceMatcher(None, str(FSM), (str(question) + str(state.generation))).ratio()
            similarities_fsms.append((str(FSM), sim))
        similarities_fsms.sort(key=lambda x: x[1], reverse=True)
        selectedFSMs = [FSM for FSM, _ in similarities_fsms[:2]]

        # extract code FSMs
        curr_fsms = fsm_generate(model, None, state.generation, program_name)

        analysis_chain_oai = execution_analysis_chain(model)
        analysis_solution = analysis_chain_oai.invoke(
            {"curr_code":str(state.generation), "curr_FSMs": str(curr_fsms), "ref_FSMs": str(selectedFSMs)}
        )
 
        file_path = '../output/analysis_report.txt'

        with open(file_path, 'w') as file:
            file.write(analysis_solution.report)

        messages += [
            (
            "assistant", 
            f"You need to refer to the execution error analysis report: {str(analysis_solution.report)}"
            ) 
        ]

    if isuserreq: 
        # permit user requestments
        if usereq != None:
            messages += [
                (
                "assistant", 
                f"You need to also refer to logic requestments: {str(usereq)}"
                ) 
            ]
        else:
            logger.info("userreq do not exist")

    if iscontext and iterations > 0:

        # context-aware
        logger.info(f"[{process_id}] start thinking: {iterations}")
        context_chain_oai = context_aware_chain(model)
        context_solution = context_chain_oai.invoke(
        {"code": state.generation, "docs": concatenated_content, "problem": question}
        )
        logger.info(f"Thinking 1: relevant headers and apis: {context_solution.imports}")
        
        def is_valid_header(header):
            if re.match(r'^[\w\-.]+\.h(pp)?$', header):
                return True
            return False

        def is_valid_api(api):
            if re.match(r'^[A-Za-z_]\w*$', api):
                return True
            return False

        for header in context_solution.imports:
            if is_valid_header(header) == False:
                continue
            for imports in selectedimpots:
                if header == imports and header not in whitelist:
                    whitelist.append(header)
            else:
                if header not in blacklist:
                    blacklist.append(header)

        for api in context_solution.apis:
            if is_valid_api(api) == False:
                continue
            if str(api) in str(concatenated_content):
                if api not in whitelist:
                    whitelist.append(api)                                                              
            else:
                if api not in blacklist:
                    blacklist.append(api)
                    
        logger.info(f"[{process_id}] Thinking 2: whitelist: {whitelist}")

        similarities_headers = []
        whitelist.append(f"{question}")
        for con_header in selectedimpots:
            raw_con_header = con_header
            con_header = con_header.split('/')[-1]
            if con_header.endswith('.h'):
                con_header_temp = con_header[:-2]
            else:
                con_header_temp = con_header
            if whitelist: 
                sim = max(substring_similarity(con_header_temp.lower(), item.lower()) for item in whitelist)
                similarities_headers.append((raw_con_header, sim))

        similarities_headers.sort(key=lambda x: x[1], reverse=True)
        extend_headers = max(1, int(len(similarities_headers)))
        extend_headers = [header for header, score in similarities_headers[:extend_headers] if score >= 3]
        raw_len = len(whitelist)
       
        for header in extend_headers:
            if header not in whitelist:
                whitelist.append(header)
            if len(whitelist) > raw_len + 10:
                break
        logger.info(f"[{process_id}] Thinking 3: extended whitelist for headers: {whitelist}")
        
        is_extend_api = False
        if is_extend_api: 
            similarities_api = []
            for con_api in selectedapis:
                if whitelist: 
                    sim = max(substring_similarity(con_api.lower(), item.lower()) for item in whitelist)
                    similarities_api.append((con_api, sim))
            similarities_api.sort(key=lambda x: x[1], reverse=True)
            # print(similarities_api)
            extend_apis = max(1, int(len(similarities_api)))
            extend_apis = [header for header, score in similarities_api[:extend_apis] if score >= 3]
            raw_len = len(whitelist)
        
            for api in extend_apis:
                if api not in whitelist:
                    whitelist.append(api)
                if len(whitelist) > raw_len + 100:
                    break
            logger.info(f"[{process_id}] Thinking 3: extended whitelist for apis {whitelist}")

        llm_enable = False
        if llm_enable:
            graph_chain_oai = graph_create_chain(model)
            graph_solution = graph_chain_oai.invoke(
                {"question": str(question) + str(state.generation), "list":  whitelist}
            )
            score_list = graph_solution.relationship
        else:
            score_list = []
            api_headers = whitelist.copy()
            api_headers.append(str(question))
            for i in api_headers:
                for j in api_headers:
                    if i != j:
                        if i.endswith('.h') and j.endswith('.h'):
                            score = substring_similarity(i[:-2].lower(), j[:-2].lower())
                        else:
                            score = substring_similarity(i.lower(), j.lower())
                        
                        score_list.append([str(i), str(j), float(score)])

        logger.info(f"[{process_id}] Thinking 4: dependency graph end")
        if score_list != None:
            correct_headers, correct_apis = graphinfer(score_list)
        logger.info(f"[{process_id}] Thinking 5: correct headers or apis: {whitelist}")

        whitelist = []
        whitelist.extend(correct_headers)
        whitelist.extend(correct_apis)
        
    
        messages += [
            (
                "user",
                f"Your answer cannot contain the provided headers and apis from blacklist: {str(blacklist)}"
            )
        ]

        messages += [
            (   
                "user",
                f"Your answer must contain all the headers and apis in the whitelist: {str(whitelist)}!"
            )
        ]


        logger.info(f"end thinking: {iterations}")

    logger.info(f"[{process_id}] start generate code: {iterations}")

    # update rag content
    
    if os_type == "RIOT":
        print("RIOT Docs.")
        ragimports_new = rag("../datasets/imports_riot.csv")
        ragapis_new = rag("../datasets/api_riot.csv")
    elif os_type == "Zephyr":
        print("Zephyr Docs.")
        ragimports_new = rag("../datasets/imports_zephyr.csv")
        ragapis_new = rag("../datasets/api_zephyr.csv")
    elif os_type == "Contiki":
        print("Contiki Docs.")
        ragimports_new = rag("../datasets/imports_contiki.csv")
        ragapis_new = rag("../datasets/api_contiki.csv")  
    elif os_type == "FreeRTOS":
        print("FreeRTOS Docs.")
        ragimports_new = rag("../datasets/imports_freertos.csv")
        ragapis_new = rag("../datasets/api_freertos.csv")
    selectedapis_new = search_topk_difflib(ragapis_new, question, state.generation, 1)
    selectedimports_new = search_topk_difflib(ragimports_new, question, state.generation, 1)
    
    # concatenated_content_new = str(selectedapis_new + selectedimports_new)
    
    concatenated_content_new = ""
    for con_api in selectedapis_new:
        for cor_header in correct_headers:
            if str(cor_header) in str(con_api):
                if con_api not in concatenated_content_new:
                    concatenated_content_new += str(con_api)
                    concatenated_content_new += "\n"
                    break
        for cor_api in correct_apis:
            if str(cor_api) in str(con_api):
                if con_api not in concatenated_content_new:
                    concatenated_content_new += str(con_api)
                    concatenated_content_new += "\n"
                    break
    for con_import in selectedimports_new:
        for cor_header in correct_headers:
            if str(cor_header) in str(con_import):
                if con_import not in concatenated_content_new:
                    concatenated_content_new += str(con_import)
                    concatenated_content_new += "\n"
                    break   
        for cor_api in correct_apis:
            if str(cor_api) in str(con_import):
                if con_import not in concatenated_content_new:
                    concatenated_content_new += str(con_import)
                    concatenated_content_new += "\n"
                    break
            
    if iterations == 0 or concatenated_content_new == "":
        content = search_topk_difflib(ragapis, question, state.generation, 0.25)
        concatenated_content_new = content

    # print(concatenated_content_new)
    
    if model == "gpt-4o":
        code_gen_chain_oai = openaichain(model)
        code_solution = code_gen_chain_oai.invoke(
            {"context": concatenated_content_new, "messages": messages}
        )
        print(messages)
        messages += [
            (
                "assistant",
                f"prefix: {code_solution.prefix} \n block: {code_solution.block} \n"
            )
        ]
    elif model == "deepseek-coder":

        def format_output4deepseek(res):
            code_res = ""
            if "```c" in res:
                code_res = res[res.find("```c") + len("```c"):]
                code_res = code_res[:code_res.find("```")]
            else:
                logger.error("generate code fail!")
            return CodeDeepseek(block=code_res)
        
        code_gen_chain_oai = deepseekchain(model)
        code_solution = code_gen_chain_oai.invoke(
            {"context": concatenated_content_new, "messages": messages}
        )
        code_solution = format_output4deepseek(code_solution.content)
        
    elif model == "deepseek-reasoner":
        
        def format_output4deepseek(res):
            code_res = ""
            if "```c" in res:
                code_res = res[res.find("```c") + len("```c"):]
                code_res = code_res[:code_res.find("```")]
            else:
                logger.error("generate code fail!")
            return CodeDeepseek(block=code_res)
        
        code_gen_chain_oai = deepseekchain(model)
        code_solution = code_gen_chain_oai.invoke(
            {"context": concatenated_content_new, "messages": messages}
        )
        code_solution = format_output4deepseek(code_solution.content)
        print(messages)
        
    else:
        logger.error("generate code fail!")
        return {"generate": 0}

    state.generation = code_solution.block
    logger.info(f"[{process_id}] end generate code: {iterations}")
    
    # remove_header_apis_chain_oai = remove_header_apis_chain(model)
    # remove_header_apis_solution = remove_header_apis_chain_oai.invoke(
    #     {"question": str(question), "code": str(state.generation)}
    # )
    # state.generation = remove_header_apis_solution.block
    
    file_path = '../output/'+program_name+'/'+str(process_id)+'/'+str(method_type)+'/'+program_name+'_'+str(role)+'_'+str(state.iterations)+'_solution.c'
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(state.generation)
    logger.step(f"[{program_name}] code generation completed for iteration {iterations}")
    state.iterations += 1
    return {"generate": 1}

def injected_code_gen(model, state, question):

    logger.info("start inject logs")

    pre_code = state.generation

    FSMS_json = create_fsms()
    similarities_fsms = []
    
    for FSM in FSMS_json:
        sim = difflib.SequenceMatcher(None, str(FSM), (str(question) + str(state.generation))).ratio()
        similarities_fsms.append((str(FSM), sim))

    similarities_fsms.sort(key=lambda x: x[1], reverse=True)
    selectedFSMs = [FSM for FSM, _ in similarities_fsms[:1]]

    inject_chain_oai = execution_inject_chain(model)
    inject_solution = inject_chain_oai.invoke(
        {"FSMs": selectedFSMs, "Code": pre_code}
    )

    state.generation = inject_solution.block

    file_path = '../output/inject_solution.c'

    with open(file_path, 'w') as file:
        file.write(state.generation)
    logger.info("end inject logs")

    return inject_solution.block


def refine_code(model, state, question):

    logger.info("start refine code")
    FSMS_json = create_fsms()
    similarities_fsms = []
    log = state.runtimelogs
    for FSM in FSMS_json:
        sim = difflib.SequenceMatcher(None, str(FSM), (str(question) + str(state.generation))).ratio()
        similarities_fsms.append((str(FSM), sim))

    similarities_fsms.sort(key=lambda x: x[1], reverse=True)
    selectedFSMs = [FSM for FSM, _ in similarities_fsms[:2]]

    code = state.generation
    code_refine_chain_oai = code_refine_chain(model)
    refine_solution = code_refine_chain_oai.invoke(
        {"FSMs": selectedFSMs, "code": code, "logs": log}
    )

    state.generation = refine_solution.block

    logger.info("-end refine code")
    return refine_solution.block


def compiler(
    state: CodeState,
    hw_type: str,
    os_type: str
) -> Dict[str, int]:
    """Compile code for the target hardware and operating system.
    
    Args:
        state: Current code state
        hw_type: Target hardware type
        os_type: Target operating system
        
    Returns:
        Dictionary containing compilation status
    """
    main_code = state.generation

    def write_code(filepath, code):
        try:
            with open(filepath, "w") as f:
                f.write(code)
            return True
        except Exception as e:
            logging.error(f"Error writing C code to file: {e}")
            return False

    def run_local_command(command, cwd):
        try:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            logging.error(f"Error during local command execution: {e}")
            return None

    def run_remote_command(ssh_client, command):
        
        try:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            return stdout.read().decode() + stderr.read().decode()
        except Exception as e:
            logging.error(f"Error during remote command execution: {e}")
            return None


    def check_errors(output, error_patterns):
        for pattern in error_patterns:
            errors = pattern.findall(output)
            if errors:
                return [remove_ansi_escape_sequences(text) for text in errors], "not pass"
        return [], "pass"

    if hw_type == "esp32":
        
        if os_type == "Contiki":
            remote_filepath = "/home/XXX/contiki-ng/my/hello-world/hello-world.c"
            build_command = (
                "docker exec -i ac7a617cc2af /bin/bash -c 'cd /home/user/contiki-ng/my/hello-world && make TARGET=zoul'"
            )
            error_patterns = [
                re.compile(r".*Stop.*", re.MULTILINE),
                re.compile(r".*error:.*", re.MULTILINE)
            ]

            # SSH Details
            ssh_host = "10.193.36.109"
            ssh_port = 2200
            ssh_username = "XXX"
            ssh_password = "123456" 

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                print("Get Lock successfully")
                ssh_client.connect(ssh_host, port=ssh_port, username=ssh_username, password=ssh_password)
                
                sftp = ssh_client.open_sftp()
                try:
                    with sftp.open(remote_filepath, "w") as remote_file:
                        remote_file.write(main_code)
                except Exception as e:
                    logging.error(f"Error writing C code to remote file: {e}")
                    return {"compiler": 0}
                finally:
                    sftp.close()
                
                remote_command = f"{build_command}"
                output = run_remote_command(ssh_client, remote_command)
                # print(output)
                errors, errorstate = check_errors(output, error_patterns)
                # print(errors, errorstate)
                state.error = errors
                state.errorstate = errorstate

                return {"compiler": 1}
            except Exception as e:
                logging.error(f"SSH connection error: {e}")
                return {"compiler": 0}
            finally:
                ssh_client.close()
            
        elif os_type == "Zephyr":
            
            remote_filepath = "E:\\local_code\\IoT\\zephyrproject\\zephyr\\my\\LLM_Gen\\src\\main.c"
            build_command = (
                'powershell -Command "conda activate zephyr; cd E:\\local_code\\IoT\\zephyrproject; west build -p always -b esp32_devkitc_wroom E:\\local_code\\IoT\\zephyrproject\\zephyr\\my\\LLM_Gen"'
            )
            error_patterns = [
                re.compile(r".*Stop.*", re.MULTILINE),
                re.compile(r".*error:.*", re.MULTILINE)
            ]
            cwd = "E:\\local_code\\IoT\\zephyrproject\\zephyr"
            conda_env = "zephyr"  

            # SSH Details
            ssh_host = "10.214.131.123"
            ssh_port = 22000
            ssh_username = "XXX"
            ssh_password = "tkk88965" 

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                with lock:
                    print("Get Lock successfully")
                    ssh_client.connect(ssh_host, port=ssh_port, username=ssh_username, password=ssh_password)
                    
                    sftp = ssh_client.open_sftp()
                    try:
                        with sftp.open(remote_filepath, "w") as remote_file:
                            remote_file.write(main_code)
                    except Exception as e:
                        logging.error(f"Error writing C code to remote file: {e}")
                        return {"compiler": 0}
                    finally:
                        sftp.close()
                    
                    remote_command = f"{build_command}"
                    
                    
                    output = run_remote_command(ssh_client, remote_command)
                    # print(output)

                    errors, errorstate = check_errors(output, error_patterns)
                    state.error = errors
                    state.errorstate = errorstate

                return {"compiler": 1}
            
            except Exception as e:
                logging.error(f"SSH connection error: {e}")
                return {"compiler": 0}
            finally:
                ssh_client.close()

        elif os_type == "RIOT":

            filepath = "/root/RIOT/examples/LLM_Gen/main.c"
            build_command = ["make"]
            error_patterns = [
                re.compile(r".*Stop.*", re.MULTILINE),
                re.compile(r".*error:.*", re.MULTILINE)
            ]
            cwd = "/root/RIOT/examples/LLM_Gen"

            if not write_code(filepath, main_code):
                return {"compiler": 0}

            output = run_local_command(build_command, cwd)

            errors, errorstate = check_errors(output, error_patterns)
            state.error = errors
            state.errorstate = errorstate

            return {"compiler": 1}
        
        elif os_type == "FreeRTOS":
            
            remote_filepath = "E:\\local_code\\IoT\\esp32-freertos\\idf_test\\main\\main.c"
            build_command = (
                'powershell -Command "idf4ps; cd E:\\local_code\\IoT\\esp32-freertos\\idf_test; idf.py build"'
            )
            error_patterns = [
                re.compile(r".*Stop.*", re.MULTILINE),
                re.compile(r".*error:.*", re.MULTILINE)
            ]
            cwd = "E:\\local_code\\IoT\\esp32-freertos\\idf_test"
            conda_env = "esp32"  

            # SSH Details
            ssh_host = "10.214.131.123"
            ssh_port = 2222
            ssh_username = "wop88"
            ssh_password = "tkk88965" 

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                with lock:
                    ssh_client.connect(ssh_host, port=ssh_port, username=ssh_username, password=ssh_password)
                    
                    sftp = ssh_client.open_sftp()
                    try:
                        with sftp.open(remote_filepath, "w") as remote_file:
                            remote_file.write(main_code)
                    except Exception as e:
                        logging.error(f"Error writing C code to remote file: {e}")
                        return {"compiler": 0}
                    finally:
                        sftp.close()
                    remote_command = f"{build_command}"
                    output = run_remote_command(ssh_client, remote_command)
                    # print(output)

                    errors, errorstate = check_errors(output, error_patterns)
                    state.error = errors
                    state.errorstate = errorstate

                return {"compiler": 1}
            
            except Exception as e:
                logging.error(f"SSH connection error: {e}")
                return {"compiler": 0}
            finally:
                ssh_client.close()
                
        else:
            logging.warning("Unsupported hardware type")
            return {"compiler": 0}
    else:
        logging.warning("Unsupported hardware type")
        return {"compiler": 0}

def executor(state, duration):

    def readlog(duration):
        ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
        start_time = time.time()
        data = []
        try:
            while True:
                if time.time() - start_time > duration:
                    break
                if ser.in_waiting > 0:
                    line = ser.readline()
                    data.append(line.decode('utf-8'))
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            ser.close()
        return str(data)

    try:
        build_command = ["make", "flash"]
        result = subprocess.run(build_command, cwd="/root/RIOT/examples/LLM_Gen", capture_output=True, text=True)
        if result.returncode == 0:
            logdata = readlog(duration)
            print(logdata)
        else:
            print("Flashing failed:", result.stderr)
        print(logdata)
    except Exception as e:
        logger.error(f"Error during build process: {e}")

    state.runtimelogs = str(logdata)
    return logdata

def data_loader(data_file):

    data_dict = {}
    try:
        with open(data_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    code_name = row['code_name']
                    problem = row['problem']
                    data_dict[code_name] = problem
                except Exception as e:
                    logger.error(f"An error occurred while processing the row: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    return data_dict

def code_gen4SELFDEBUG(process_id, model, state, vectorstore, question, program_name, role, device_type, os_type):
    # basline

    state.messages = []
    messages = state.messages
    iterations = state.iterations
    errorstate = state.errorstate
    error = state.error

    messages += [
      (
        "user",
        f"{question}"
      )
    ]

    if errorstate == "not pass":
        messages += [
        (
            "user",
            f"Now, try again. Check the error information: {error} and Invoke the code tool to solve the error and structure the output with a prefix and code block."
        )
        ]

    # RAG: imports and apis
    rate_apis = 0.25
    if os_type == "RIOT":
        ragapis = rag("../datasets/api_riot.csv")
    elif os_type == "Zephyr":
        ragapis = rag("../datasets/api_zephyr.csv")
    elif os_type == "Contiki":
        ragapis = rag("../datasets/api_contiki.csv") 
    elif os_type == "FreeRTOS":
        
        ragapis = rag("../datasets/api_freertos.csv")
        
    selectedapis = search_topk_difflib(ragapis, question, state.generation, rate_apis)
    concatenated_content = str(selectedapis)

    if model == "gpt-4o":
        
        code_gen_chain_oai = openaichain(model)
        code_solution = code_gen_chain_oai.invoke(
            {"context": concatenated_content, "messages": messages}
        )
        messages += [
            (
                "assistant",
                f"prefix: {code_solution.prefix} \n block: {code_solution.block} \n"
            )
        ]
        
    elif model == "deepseek-coder":

        def format_output4deepseek(res):
            code_res = ""
            if "```c" in res:
                code_res = res[res.find("```c") + len("```c"):]
                code_res = code_res[:code_res.find("```")]
            else:
                logger.error("generate code fail!")
            return CodeDeepseek(block=code_res)
        
        code_gen_chain_oai = deepseekchain(model)
        code_solution = code_gen_chain_oai.invoke(
            {"context": concatenated_content, "messages": messages}
        )
        code_solution = format_output4deepseek(code_solution.content)
    else:
        return {"generate": 0}
    
    state.generation = code_solution.block
    print(f"end generate code: {program_name}, {iterations}")
    

    file_path = '../output/'+program_name+'/'+str(process_id)+'/'+str("deepseek-coder-selfdebug")+'/'+program_name+'_'+str(role)+'_'+str(state.iterations)+'_solution.c'
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(state.generation)
    state.iterations += 1
    return {"generate": 1}

def code_gen4Auto_cot(process_id, model, state, vectorstore, question, program_name, role, device_type, os_type):
    # baseline
    state.messages = []
    messages = state.messages
    iterations = state.iterations
    errorstate = state.errorstate
    error = state.error

    messages += [
      (
        "user",
        f"{question}"
      )
    ]
  
    # RAG: imports and apis
    rate_apis = 0.15
    if os_type == "RIOT":
        ragapis = rag("../datasets/api_riot.csv")
    elif os_type == "Zephyr":
        ragapis = rag("../datasets/api_zephyr.csv")
    elif os_type == "Contiki":
        ragapis = rag("../datasets/api_contiki.csv") 
    elif os_type == "FreeRTOS":
        ragapis = rag("../datasets/api_freertos.csv")
    selectedapis = search_topk_difflib(ragapis, question, state.generation, rate_apis)
    concatenated_content = str(selectedapis)

    logger.info(f"start generate code: {iterations}")

    if model == "gpt-4o":
        code_gen_chain_oai = openaichain(model)
        code_solution = code_gen_chain_oai.invoke(
            {"context": concatenated_content, "messages": messages}
        )
        messages += [
            (
                "assistant",
                f"prefix: {code_solution.prefix} \n block: {code_solution.block} \n"
            )
        ]
    elif model == "deepseek-coder":

        def format_output4deepseek(res):
            code_res = ""
            if "```c" in res:
                code_res = res[res.find("```c") + len("```c"):]
                code_res = code_res[:code_res.find("```")]
            else:
                logger.error("generate code fail!")
            return CodeDeepseek(block=code_res)
        
        code_gen_chain_oai = deepseekchain(model)
        code_solution = code_gen_chain_oai.invoke(
            {"context": concatenated_content, "messages": messages}
        )
        code_solution = format_output4deepseek(code_solution.content)
    else:
        return {"generate": 0}
    
    state.generation = code_solution.block
    logger.info(f"end generate code: {iterations}")
    

    file_path = '../output/'+program_name+'/'+str(process_id)+'/'+str("gpt4o-autocot")+'/'+program_name+'_'+str(role)+'_'+str(state.iterations)+'_solution.c'
    print(file_path)
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(state.generation)
    state.iterations += 1
    return {"generate": 1}

def code_gen4Direct(process_id, model, state, vectorstore, question, program_name, role):
    # direct
    state.messages = []
    messages = state.messages
    iterations = state.iterations
    errorstate = state.errorstate
    error = state.error

    messages += [
      (
        "user",
        f"{question}"
      )
    ]
    print(f"start generate code: {program_name}, {iterations}")
    concatenated_content = ""
    if model == "gpt-4o":
        code_gen_chain_oai = openaichain(model)
        code_solution = code_gen_chain_oai.invoke(
            {"context": concatenated_content, "messages": messages}
        )
        messages += [
            (
                "assistant",
                f"prefix: {code_solution.prefix} \n block: {code_solution.block} \n"
            )
        ]
    elif model == "deepseek-coder":

        def format_output4deepseek(res):
            code_res = ""
            if "```c" in res:
                code_res = res[res.find("```c") + len("```c"):]
                code_res = code_res[:code_res.find("```")]
            else:
                logger.error("generate code fail!")
            return CodeDeepseek(block=code_res)
        
        code_gen_chain_oai = deepseekchain(model)
        code_solution = code_gen_chain_oai.invoke(
            {"context": concatenated_content, "messages": messages}
        )
        code_solution = format_output4deepseek(code_solution.content)
    else:
        return {"generate": 0}
    state.generation = code_solution.block
    print(f"end generate code: {program_name}, {iterations}")
    
    file_path = '../output/'+program_name+'/'+str(process_id)+'/'+str("gpt4o-direct")+'/'+program_name+'_'+str(role)+'_'+str(state.iterations)+'_solution.c'
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(state.generation)
    state.iterations += 1
    return {"generate": 1}

def merge_sim(question, whitelist):

    def write_list_to_file(filename, score_list):
        with open(filename, 'w') as file:
            for item in score_list:
                file.write(json.dumps(item) + "\n")
                
    question = "Give me a mqtt-based application"
    whitelist = ["esp_wifi_start",
    "NetworkInit",
    "paho_mqtt.h",
    "MQTTPublish",
    "MQTTClient.h",
    "emcute_con",
    "inet_pton"]


    graph_chain_oai = graph_create_chain("gpt-4o")
    graph_solution = graph_chain_oai.invoke(
        {"question": str(question), "list":  whitelist}
    )
    score_list_1 = graph_solution.relationship

    score_list_2 = []

    explain_chain_oai = explain_create_chain("gpt-4o")
    explain_solution = explain_chain_oai.invoke(
        {"list":  whitelist}
    )
    whitelist_explain = explain_solution.explain


    for i in range(0,len(whitelist)):
        for j in range(0,len(whitelist)):
            if whitelist[i] != whitelist[j]:
                from sklearn.metrics.pairwise import cosine_similarity  
                from sklearn.feature_extraction.text import TfidfVectorizer 
                vectorizer = TfidfVectorizer().fit_transform([whitelist_explain[i].lower(), whitelist_explain[j].lower()])
                cosine_sim = cosine_similarity(vectorizer[0:1], vectorizer[1:2]) 
                # score = substring_similarity_rate(whitelist_explain[i].lower(), whitelist_explain[j].lower())
                score_list_2.append([whitelist[i], whitelist[j], float(cosine_sim[0][0])])

    write_list_to_file("score_list_1.txt", score_list_1)
    write_list_to_file("score_list_2.txt", score_list_2)

    score_list_3 = []

    score_dict_1 = {(item1, item2): score for item1, item2, score in score_list_1}

    for item1, item2, score2 in score_list_2:
        score1 = score_dict_1.get((item1, item2), 0)
        total_score = score1 + score2
        score_list_3.append([item1, item2, total_score])

    # print(score_list_3)

    write_list_to_file("score_list_3.txt", score_list_3)


def eval():
    import json
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    import networkx as nx
    def read_score_list_from_file(filename):
        score_list = []
        with open(filename, 'r') as file:
            for line in file:
                score_list.append(json.loads(line.strip()))
        return score_list

    def normalize_scores(score_list):
        scores = [score for _, _, score in score_list]
        min_score = min(scores)
        max_score = max(scores)
        
        for i in range(len(score_list)):
            if max_score != min_score:
                normalized_score = (score_list[i][2] - min_score) / (max_score - min_score)
            else:
                normalized_score = 0  
            score_list[i][2] = normalized_score
        return score_list

    def create_heatmap(score_list, title):
        items = sorted(set(item for item_pair in score_list for item in item_pair[:2]))
        data = pd.DataFrame(0, index=items, columns=items)
        
        for item1, item2, score in score_list:
            data.at[item1, item2] = score
            data.at[item2, item1] = score  

        plt.figure(figsize=(16, 12))
        # Create numerical labels for the axes
        numeric_labels = list(range(1, len(items) + 1))
        
        ax = sns.heatmap(data, annot=True, cmap='coolwarm', fmt=".2f", annot_kws={"size": 35},
                    xticklabels=numeric_labels, yticklabels=numeric_labels)
        
        # Configure the ticks
        plt.xticks(fontsize=35)
        plt.yticks(fontsize=35)

        cbar = ax.collections[0].colorbar
        cbar.ax.tick_params(labelsize=20)
        
        plt.savefig(title + ".pdf")
        plt.show()

    def create_graph(score_list, title):
        G = nx.Graph()
        for item1, item2, score in score_list:
            if score > 0: 
                G.add_edge(item1, item2, weight=score)

        edges_with_weights = [(u, v, d['weight']) for u, v, d in G.edges(data=True)]
        edges_with_weights.sort(key=lambda x: x[2], reverse=True)
        top_20_percent = int(len(edges_with_weights) * 0.3)
        top_edges = edges_with_weights[:top_20_percent]

        G_top = nx.Graph()
        G_top.add_weighted_edges_from(top_edges)

        pos = nx.spring_layout(G_top)  
        edges, weights = zip(*nx.get_edge_attributes(G_top, 'weight').items())

        plt.figure(figsize=(10, 8))
        nx.draw(G_top, pos, node_color='lightblue', with_labels=True, node_size=2000, font_size=15)
        nx.draw_networkx_edges(G_top, pos, edgelist=edges, width=[w * 2 for w in weights])  
        plt.savefig(title + "_top20_graph.pdf")
        plt.show()

    score_list_1 = read_score_list_from_file("score_list_1.txt")
    score_list_2 = read_score_list_from_file("score_list_2.txt")
    score_list_3 = read_score_list_from_file("score_list_3.txt")
    score_list_4 = read_score_list_from_file("score_list_4.txt")

    score_list_1 = normalize_scores(score_list_1) 
    score_list_2 = normalize_scores(score_list_2)

    score_dict_1 = {(item1, item2): score for item1, item2, score in score_list_1}

    score_list_3 = []
    for item1, item2, score2 in score_list_2:
        score1 = score_dict_1.get((item1, item2), 0)
        total_score = score1 + score2
        score_list_3.append([item1, item2, total_score])

    score_list_3 = normalize_scores(score_list_3)

    create_heatmap(score_list_1, "Heatmap for Score List 1")
    create_heatmap(score_list_2, "Heatmap for Score List 2 (Normalized)")
    create_heatmap(score_list_3, "Heatmap for Score List 3 (Combined and Normalized)")
    create_heatmap(score_list_4, "Heatmap for Score List 4")

    create_graph(score_list_1, "Graph for Score List 1")
    create_graph(score_list_2, "Graph for Score List 2 (Normalized)")
    create_graph(score_list_3, "Graph for Score List 3 (Combined and Normalized)")
    create_graph(score_list_4, "Graph for Score List 4")
