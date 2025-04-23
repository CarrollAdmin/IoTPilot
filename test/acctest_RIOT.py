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
    r'#include\s*[<"]paho_mqtt\.h[>"]',
    r'#include\s*[<"]MQTTClient\.h[>"]'
]

apis_RIOT_MQTT = [
    r'\bMQTTClient\b',
    r'\bMQTTMessage\b',
    r'\bMQTTPacket_connectData\b',
    r'\bMQTTClientInit\b',
    r'\bMQTTConnect\b',
    r'\bMQTTPublish\b'
]

headers_RIOT_COAP = [
    r'#include\s*[<"]net/gcoap\.h[>"]',
    r'#include\s*[<"]arpa/inet\.h[>"]'
]

apis_RIOT_COAP = [
    r'\bgcoap_req_init\b',
    r'\binet_pton\b',
    r'\bgcoap_req_send\b',
]

headers_RIOT_MQTT_SN = [
    r'#include\s*[<"]net/emcute\.h[>"]',
    r'#include\s*[<"]arpa/inet\.h[>"]'
]

apis_RIOT_MQTT_SN  = [
    r'\bemcute_con\b',
    r'\bemcute_pub\b',
    r'\binet_pton\b'
]

headers_RIOT_IRQ= [

]

apis_RIOT_IRQ  = [
    r'\birq_restore\b',
    r'\birq_disable\b',

]

headers_RIOT_RTC = [
    r'#include\s*[<"]periph/rtc\.h[>"]',
]

apis_RIOT_RTC  = [
    r'\brtc_get_time\b',
    r'\brtc_set_alarm\b',
]

headers_RIOT_UDP = [
    r'#include\s*[<"]sys/socket\.h[>"]',
    r'#include\s*[<"]arpa/inet\.h[>"]',
]

apis_RIOT_UDP  = [
    r'\binet_pton\b',
    r'\bsendto\b',
    r'\bsocket\b',
]

headers_RIOT_Thread = [
    r'#include\s*[<"]thread\.h[>"]',
]

apis_RIOT_Thread  = [
    r'\bthread_create\b',
    r'\bmsg_send\b',
    r'\bmsg_receive\b',
]

headers_RIOT_Timer = [
    r'#include\s*[<"]xtimer\.h[>"]',
    r'#include\s*[<"]periph/gpio\.h[>"]',
]

apis_RIOT_Timer  = [
    r'\btimer_set\b',
    r'\bgpio_init\b',
    r'\bgpio_toggle\b',
]

headers_RIOT_Flash = [
    r'#include\s*[<"]nvs_flash\.h[>"]',
    r'#include\s*[<"]nvs\.h[>"]',
]

apis_RIOT_Flash  = [
    r'\bnvs_commit\b',
    r'\bnvs_flash_init\b',
    r'\bnvs_open\b',
    r'\bnvs_close\b',
]

headers_RIOT_MMA = [
    r'#include\s*[<"]mma8x5x\.h[>"]',
    r'#include\s*[<"]mma8x5x_params\.h[>"]',
]

apis_RIOT_MMA  = [
    r'\bmma8x5x_read\b',
    r'\bmma8x5x_init\b',
]

headers_RIOT_Event = [
    r'#include\s*[<"]nevent/periodic_callback\.h[>"]',
    r'#include\s*[<"]event/thread\.h[>"]',
]

apis_RIOT_Event  = [
    r'\bevent_periodic_callback_init\b',
    r'\bevent_periodic_callback_start\b',
]

headers_RIOT_DHT11 = [
    r'#include\s*[<"]dht\.h[>"]',
    r'#include\s*[<"]dht_params\.h[>"]',
]

apis_RIOT_DHT11   = [
    r'\bdht_read\b',
    r'\bdht_init\b',
]

headers_RIOT_Warn = [
    r'#include\s*[<"]dht\.h[>"]',
    r'#include\s*[<"]dht_params\.h[>"]',
    r'#include\s*[<"]periph/gpio\.h[>"]',
]

apis_RIOT_Warn  = [
    r'\dht_read\b',
    r'\bdht_init\b',
    r'\bgpio_init\b',
    r'\bgpio_clear\b',
    r'\bgpio_set\b',
]

headers_RIOT_Sched = [
    r'#include\s*[<"]sched\.h[>"]',
]

apis_RIOT_Sched  = [
    r'\bthread_create\b',
    r'\bsched_change_priority\b',
]

headers_RIOT_MBOX = [
    r'#include\s*[<"]mbox\.h[>"]',
    r'#include\s*[<"]msg\.h[>"]',
]

apis_RIOT_MBOX  = [
    r'\bmbox_get\b',
    r'\bmbox_init\b',
    r'\bmbox_put\b',
]

mapping = {
    "RIOT_MQTT": (headers_RIOT_MQTT, apis_RIOT_MQTT),
    "RIOT_COAP": (headers_RIOT_COAP, apis_RIOT_COAP),
    "RIOT_MQTT_SN": (headers_RIOT_MQTT_SN, apis_RIOT_MQTT_SN),
    "RIOT_IRQ": (headers_RIOT_IRQ, apis_RIOT_IRQ),
    "RIOT_RTC": (headers_RIOT_RTC, apis_RIOT_RTC),
    "RIOT_UDP": (headers_RIOT_UDP, apis_RIOT_UDP),
    "RIOT_Thread": (headers_RIOT_Thread, apis_RIOT_Thread),
    "RIOT_Timer": (headers_RIOT_Timer, apis_RIOT_Timer),
    "RIOT_Flash": (headers_RIOT_Flash, apis_RIOT_Flash),
    "RIOT_MMA": (headers_RIOT_MMA, apis_RIOT_MMA),
    "RIOT_Event": (headers_RIOT_Event, apis_RIOT_Event),
    "RIOT_DHT11": (headers_RIOT_DHT11, apis_RIOT_DHT11),
    "RIOT_Warn": (headers_RIOT_Warn, apis_RIOT_Warn),
    "RIOT_Sched": (headers_RIOT_Sched, apis_RIOT_Sched),
    "RIOT_MBOX": (headers_RIOT_MBOX, apis_RIOT_MBOX),
}

def count_occurrences(file_content, patterns):
    """Count occurrences of each pattern in the file content."""
    return {pattern: len(re.findall(pattern, file_content)) for pattern in patterns}

def main():
    program_names = [
        "RIOT_MQTT",
        "RIOT_COAP",
        "RIOT_MQTT_SN",
        "RIOT_IRQ",
        "RIOT_RTC",
        "RIOT_UDP",
        "RIOT_Thread",
        "RIOT_Timer",
        "RIOT_Flash",
        "RIOT_MMA",
        "RIOT_Event",
        "RIOT_DHT11",
        "RIOT_Warn",
        "RIOT_Sched",
        "RIOT_MBOX"
    ]
    # program_names = [
    #     "Zephyr_MQTT",
    #     "Zephyr_COAP",
    #     # "RIOT_MQTT_SN",
    #     "Zephyr_IRQ",
    #     # "RIOT_RTC",
    #     "Zephyr_UDP",
    #     # "RIOT_Thread",
    #     # "RIOT_Timer",
    #     # "RIOT_Flash",
    #     "Zephyr_MMA",
    #     # "RIOT_Event",
    #     # "RIOT_DHT11",
    #     # "RIOT_Warn",
    #     # "RIOT_Sched",
    #     # "RIOT_MBOX"
    # ]


    iters = 5
    method_type = "deepseeker-coder"
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
                # print(f"File not found: {file_path}")
                continue  

            iter = file_content["iterations"]

            file_path = '../output/'+str(program_name)+'/'+str(dir)+'/'+str(method_type)+'/'+program_name+'_'+str(-1)+'_'+str(iter-1)+'_solution.c'

            try:
                with open(file_path, 'r') as file:
                    file_content = file.read()
            except FileNotFoundError:
                # print(f"File not found: {file_path}")
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
