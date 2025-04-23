import re
import os

def find_final_code(directory):
    new_filename = ""

    for _, _, files in os.walk(directory):
        for file in files:
            if file > new_filename:
                new_filename = file

    return new_filename

headers_Contiki_MQTT = [
    r'#include\s*[<"]mqtt.h[>"]',
    r'#include\s*[<"]mqtt-prop.h[>"]'
    r'#include\s*[<"]contiki.h[>"]'
]

apis_Contiki_MQTT = [
    r'\bmqtt_register\b',
    r'\bmqtt_connect\b',
    r'\bmqtt_publish\b'
    
]

headers_Contiki_COAP = [
    r'#include\s*[<"]coap-engine.h[>"]',
    r'#include\s*[<"]contiki.h[>"]',
    r'#include\s*[<"]net/netstack.h[>"]',

]

apis_Contiki_COAP = [
    r'\bcoap_get_payload\b',
    r'\bcoap_init_message\b',
    r'\bcoap_set_header_uri_path\b',
    r'\bcoap_set_payload\b',
    r'\bCOAP_BLOCKING_REQUEST\b',
]

headers_Contiki_led= [
    r'#include\s*[<"]dht11-sensor.h[>"]',
    r'#include\s*[<"]dev/gpio-hal.h[>"]',
    r'#include\s*[<"]contiki.h[>"]'
]

apis_Contiki_led  = [
    r'\bdht11_sensor.configure\b',
    r'\bdht11_sensor.value\b',

]


headers_Contiki_UDP = [
    r'#include\s*[<"]simple-udp.h[>"]',
    r'#include\s*[<"]uip.h[>"]',
]

apis_Contiki_UDP  = [
    r'\bsimple_udp_register\b',
    r'\bsimple_udp_sendto\b',
    r'\buip_ipaddr\b',
]


headers_Contiki_dht11 = [
    r'#include\s*[<"]dht11-sensor.h[>"]',
    r'#include\s*[<"]dev/gpio-hal.h[>"]',
]

apis_Contiki_dht11  = [
    r'\bdht11_sensor.configure\b',
    r'\bdht11_sensor.value\b',
]


mapping = {
    "Contiki_MQTT": (headers_Contiki_MQTT, apis_Contiki_MQTT),
    "Contiki_COAP": (headers_Contiki_COAP, apis_Contiki_COAP),
    "Contiki_led": (headers_Contiki_led, apis_Contiki_led),
    "Contiki_UDP": (headers_Contiki_UDP, apis_Contiki_UDP),
    "Contiki_DHT11": (headers_Contiki_dht11, apis_Contiki_dht11),
}

def count_occurrences(file_content, patterns):
    """Count occurrences of each pattern in the file content."""
    return {pattern: len(re.findall(pattern, file_content)) for pattern in patterns}

def main():

    program_names = [  
        "Contiki_DHT11",
        "Contiki_led",
        "Contiki_UDP",
        "Contiki_COAP",
        "Contiki_MQTT",
    ]


    iters = 5
    method_type = "deepseeker-wo.execution"
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
