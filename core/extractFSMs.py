import openai  
import csv
import json
import re
import sys
sys.path.append("../utils")
import os
import logging
import time
from graphviz import Digraph

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

model = "gpt-4o"
api_base = "https://xiaoai.plus/v1"
api_key = 'sk-d7FJkaWhvDSKTuoCgFGMjoQLi1anNcbSHdrR8nPMUsLKdvRo'

def gpt4_llmcall(prompt):
    print("call gpt4")
    openai.api_base = api_base
    openai.api_key = api_key
    max_retries = 20
    retries = 0
    retry_delay = 1
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", 
                    "content": "You are a helpful AI assistant to help developers solve challenging coding problems."},
                    {"role": "user", 
                    "content": prompt}
                ],
                stream=True,
                request_timeout=60
            )
            completion_text = ""
            for chunk in response:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    choice = chunk['choices'][0]
                    if 'delta' in choice and 'content' in choice['delta']:
                        completion_text += choice['delta']['content']
            return completion_text
        except openai.error.InvalidRequestError as e:
            print(f"Invalid request error: {e}")
            break  
        except openai.error.RateLimitError as e:
            print(f"Rate limit error: {e}, retrying in {retry_delay} seconds...")
            retries += 1
            time.sleep(retry_delay)
        except openai.error.APIError as e:
            print(f"API error: {e}, retrying in {retry_delay} seconds...")
            retries += 1
            time.sleep(retry_delay)
        except (ConnectionResetError, IOError) as e:
            print(f"Connection error: {e}, retrying in {retry_delay} seconds...")
            retries += 1
            time.sleep(retry_delay)
        except Exception as e:
            print(f"Unexpected error: {e}, retrying in {retry_delay} seconds...")
            retries += 1
            time.sleep(retry_delay)
        print("Retries:", retries)
    return None

def extractFSMs(path, program):

    try:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        logging.error(f"The file {path} does not exist.")
        return
    except IOError:
        logging.error(f"An error occurred while reading the file {path}.")
        return

    try:
        with open("FSMPrompt.txt", 'r', encoding='utf-8') as file:
            prompt_template = file.read()
    except FileNotFoundError:
        logging.error(f"The file FSMPrompt.txt does not exist.")
        return
    except IOError:
        logging.error(f"An error occurred while reading the file FSMPrompt.txt.")
        return
    
    prompt = prompt_template.replace("<<Problem>>", content)
    res = gpt4_llmcall(prompt)
    # logging.info(res)
    code_res = ""
    if "```json" in res:
        code_res = res[res.find("```json") + len("```json"):]
        code_res = code_res[:code_res.find("```")]
    else:
        logging.error("generate FSMs fail!")
        return

    output_file_path = "../fsms/"+program + '_fsm.json'
    try:
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(code_res)
        logging.info(f"Result written to {output_file_path}")
    except IOError:
        logging.error(f"An error occurred while writing to the file {output_file_path}.")
        return
    
    visualize_fsm(output_file_path, program + '_fsm')

def visualize_fsm(json_file, output_name):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            fsm_data = json.load(file)
            print(fsm_data)
    except FileNotFoundError:
        logging.error(f"The file {json_file} does not exist.")
        return
    except IOError:
        logging.error(f"An error occurred while reading the file {json_file}.")
        return

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
    
    dot_file_path = "../fsms/" + output_name + '.dot'
    png_file_path = "../fsms/" + output_name + '.png'
    dot.save(dot_file_path)
    dot.render(png_file_path, format='png', cleanup=True)
    logging.info(f"FSM visualization saved as {png_file_path}")
    
if __name__ == "__main__":

    source_code = [
        "dht",
    ]
    for code in source_code:
        extractFSMs("../fsms/ref_code/"+str(code)+".c", str(code))

    
