import re
import os

def find_final_code(directory):
    new_filename = ""

    for _, _, files in os.walk(directory):
        for file in files:
            if file > new_filename:
                new_filename = file

    return new_filename

headers_FreeRTOS_MQTT = [
    r'#include\s*[<"]mqtt_client.h[>"]',
    r'#include\s*[<"]freertos/task.h[>"]',
    r'#include\s*[<"]freertos/FreeRTOS.h[>"]',
    r'#include\s*[<"]freertos/esp_wifi.h[>"]'
]

apis_FreeRTOS_MQTT = [
    r'\besp_mqtt_client_init\b',
    r'\besp_mqtt_client_start\b',
    r'\besp_mqtt_client_publish\b',
    r'\besp_wifi_start\b',
    r'\besp_wifi_set_config\b',
    r'\besp_wifi_set_mode\b'
]

headers_FreeRTOS_COAP = [
    r'#include\s*[<"]coap3/coap.h[>"]',
    r'#include\s*[<"]freertos/task.h[>"]',
    r'#include\s*[<"]freertos/FreeRTOS.h[>"]',
    r'#include\s*[<"]freertos/esp_wifi.h[>"]'
]

apis_FreeRTOS_COAP = [
    r'\bcoap_pdu_init\b',
    r'\bcoap_send\b',
    r'\bcoap_new_client_session\b',
    r'\bcoap_add_data\b',
    r'\bcoap_add_option\b',
]

headers_FreeRTOS_UDP = [
    r'#include\s*[<"]freertos/task.h[>"]',
    r'#include\s*[<"]freertos/FreeRTOS.h[>"]',
    r'#include\s*[<"]lwip/sockets.h[>"]',
    r'#include\s*[<"]lwip/netif.h[>"]',
]

apis_FreeRTOS_UDP  = [
    r'\bsocket\b',
    r'\bsendto\b',
    r'\besp_wifi_start\b',
    r'\besp_wifi_set_config\b',
    r'\besp_wifi_set_mode\b'
]


headers_FreeRTOS_FLASH = [
    r'#include\s*[<"]freertos/task.h[>"]',
    r'#include\s*[<"]freertos/FreeRTOS.h[>"]',
    r'#include\s*[<"]nvs_flash.h[>"]',
    r'#include\s*[<"]nvs.h[>"]',
]

apis_FreeRTOS_FLASH = [
    r'\bnvs_open\b',
    r'\bnvs_set_i32\b',
    r'\bnvs_commit\b',
    r'\bnvs_close\b',
]


headers_FreeRTOS_MMA = [
    r'#include\s*[<"]freertos/task.h[>"]',
    r'#include\s*[<"]freertos/FreeRTOS.h[>"]',
    r'#include\s*[<"]driver/i2c_master.h[>"]',
]

apis_FreeRTOS_MMA  = [
    r'\bi2c_master_probe\b',
    r'\bi2c_master_receive\b',
    r'\bi2c_master_bus_add_device\b',
    r'\bi2c_new_master_bus\b',
]


mapping = {
    "FreeRTOS_MQTT": (headers_FreeRTOS_MQTT, apis_FreeRTOS_MQTT),
    "FreeRTOS_COAP": (headers_FreeRTOS_COAP, apis_FreeRTOS_COAP),
    "FreeRTOS_UDP": (headers_FreeRTOS_UDP, apis_FreeRTOS_UDP),
    "FreeRTOS_FLASH": (headers_FreeRTOS_FLASH, apis_FreeRTOS_FLASH),
    "FreeRTOS_MMA": (headers_FreeRTOS_MMA, apis_FreeRTOS_MMA),
}

def count_occurrences(file_content, patterns):
    """Count occurrences of each pattern in the file content."""
    return {pattern: len(re.findall(pattern, file_content)) for pattern in patterns}

def main():

    program_names = [  
        "FreeRTOS_MQTT",
        "FreeRTOS_COAP",
        "FreeRTOS_UDP",
        "FreeRTOS_FLASH",
        "FreeRTOS_MMA",
    ]


    iters = 5
    method_type = "gpt4o-direct"
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

            iter = file_content["iterations"] - 1

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
