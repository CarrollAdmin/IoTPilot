import re
import os

def find_final_code(directory):
    new_filename = ""

    for _, _, files in os.walk(directory):
        for file in files:
            if file > new_filename:
                new_filename = file

    return new_filename

headers_RIOT_MQTT = [
    r'#include\s*[<"]zephyr/net/mqtt.h[>"]',
    r'#include\s*[<"]zephyr/net/wifi_mgmt.h[>"]'
]

apis_RIOT_MQTT = [
    r'\bmqtt_client_init\b',
    r'\bmqtt_connect\b',
    r'\bmqtt_publish\b',
    r'\bmqtt_live\b',
    r'\bnet_mgmt_init_event_callback\b',
    r'\bnet_mgmt_add_event_callback\b',
    r'\bnet_if_get_default\b',
    r'\bnet_mgmt\b',
    
]

headers_RIOT_COAP = [
    r'#include\s*[<"]zephyr/net/coap.h[>"]',
    r'#include\s*[<"]zephyr/net/wifi_mgmt.h[>"]',
    r'#include\s*[<"]zephyr/net/socket.h[>"]',
    r'#include\s*[<"]zephyr/kernel.h[>"]'

]

apis_RIOT_COAP = [
    r'\bsendto\b',
    r'\binet_pton\b',
    r'\bsocket\b',
    r'\bnet_mgmt_init_event_callback\b',
    r'\bnet_mgmt_add_event_callback\b',
    r'\bnet_if_get_default\b',
    r'\bnet_mgmt\b',
]

headers_RIOT_IRQ= [
    r'#include\s*[<"]zephyr/irq.h[>"]',
    r'#include\s*[<"]zephyr/sys/atomic.h[>"]'
]

apis_RIOT_IRQ  = [
    r'\birq_enable\b',
    r'\birq_disable\b',
    r'\birq_unlock\b',
    r'\batomic_get\b',

]


headers_RIOT_UDP = [
    r'#include\s*[<"]zephyr/net/socket.h[>"]',
    r'#include\s*[<"]zephyr/net/wifi_mgmt.h[>"]'
]

apis_RIOT_UDP  = [
    r'\binet_pton\b',
    r'\bsendto\b',
    r'\bsocket\b',
    r'\bnet_mgmt_init_event_callback\b',
    r'\bnet_mgmt_add_event_callback\b',
    r'\bnet_if_get_default\b',
    r'\bnet_mgmt\b',
]


headers_RIOT_MMA = [
    r'#include\s*[<"]zephyr/drivers/sensor.h[>"]',
    r'#include\s*[<"]zephyr/device.h[>"]',
]

apis_RIOT_MMA  = [
    r'\bdevice_get_binding\b',
    r'\bsensor_channel_get\b',
    r'\bsensor_sample_fetch\b',
    r'\bi2c_configure\b',
    r'\bi2c_get_config\b',
    r'\bi2c_read\b',
    r'\bdevice_is_ready\b',
]


mapping = {
    "Zephyr_MQTT": (headers_RIOT_MQTT, apis_RIOT_MQTT),
    "Zephyr_COAP": (headers_RIOT_COAP, apis_RIOT_COAP),
    "Zephyr_IRQ": (headers_RIOT_IRQ, apis_RIOT_IRQ),
    "Zephyr_UDP": (headers_RIOT_UDP, apis_RIOT_UDP),
    "Zephyr_MMA": (headers_RIOT_MMA, apis_RIOT_MMA),
}

def count_occurrences(file_content, patterns):
    """Count occurrences of each pattern in the file content."""
    return {pattern: len(re.findall(pattern, file_content)) for pattern in patterns}

def main():

    program_names = [
        "Zephyr_MQTT",
        "Zephyr_COAP",
        "Zephyr_IRQ",
        "Zephyr_UDP",
        "Zephyr_MMA",
    ]


    iters = 15
    method_type = "gpt4o-wo.execution"
    import json
    for program_name in program_names:
        num_headers = ""
        num_apis = ""
        for dir in range(1, iters+1):
            final_file = "-1_state.json"
            file_path = '../output/'+str(program_name)+'/'+str(dir)+'/'+str(method_type)+'/'+final_file

            try:
                with open(file_path, 'r') as file:
                    file_content = json.load(file)
            except FileNotFoundError:
                print(f"File not found: {file_path}")
                continue  

            iter = file_content["iterations"]

            file_path = '../output/'+str(program_name)+'/'+str(dir)+'/'+str(method_type)+'/'+program_name+'_'+str(-1)+'_'+str(iter)+'_solution.c'

            try:
                with open(file_path, 'r') as file:
                    file_content = file.read()
            except FileNotFoundError:
                print(f"File not found: {file_path}")
                return
            
            headers, apis = mapping[str(program_name)]
            header_counts = count_occurrences(file_content, headers)
            api_counts = count_occurrences(file_content, apis)

            correct_headers = 0
            correct_apis = 0
            for header, count in header_counts.items():
                if count > 0: correct_headers += 1

            for api, count in api_counts.items():
                if count > 0: correct_apis += 1

            num_headers += str(correct_headers)
            num_apis += str(correct_apis)

        print(f"{program_name} | method: {method_type} headers: {num_headers} | APIs: {num_apis}")

if __name__ == "__main__":
    main()
