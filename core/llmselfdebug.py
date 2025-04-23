import sys
sys.path.append('../')
from libs import *

def single_agent(process_id, model, question, max_attempts, program_name, role, device_type, os_type):
    compile_state = CodeState()
    vectorstore = None
    attempts = 0
    while compile_state.errorstate != "pass" and attempts <= max_attempts:
        attempts += 1
        code_gen4SELFDEBUG(process_id, model, compile_state, vectorstore, question, program_name, role, device_type, os_type)
        compiler(compile_state, "esp32", "FreeRTOS")
        compile_state.to_json(compile_state.iterations, -1, program_name, process_id, "deepseek-coder-selfdebug")

def main():
    process_ids = 16
    app_path = "../datasets/app.csv"
    data_dict = data_loader(app_path)
    code_names = [
        "FreeRTOS_MMA",
        "FreeRTOS_MQTT",
        "FreeRTOS_COAP",
        "FreeRTOS_UDP",
        "FreeRTOS_FLASH",
    ]
    # code_names = [  
    #     "Contiki_DHT11",
    #     "Contiki_led",
    #     "Contiki_UDP",
    #     "Contiki_COAP",
    #     "Contiki_MQTT",
    # ]
    # code_names = [  
    #     "RIOT_MQTT",
    #     "RIOT_COAP",
    #     "RIOT_MQTT_SN",
    #     "RIOT_IRQ",
    #     "RIOT_RTC",
    #     "RIOT_UDP",
    #     "RIOT_Thread",
    #     "RIOT_Timer",
    #     "RIOT_Flash",
    #     "RIOT_MMA",
    #     "RIOT_Event",
    #     "RIOT_DHT11",
    #     "RIOT_Warn",
    #     "RIOT_Sched",
    #     "RIOT_MBOX"
    #     ]
    # code_names = [  
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
    threads = []
    max_attempts = 10
    model = "deepseek-coder"
    device_type = "esp32"
    os_type = "FreeRTOS"
    for _, code_name in enumerate(code_names):
        print(f"{code_name} start generation>>>")
        role = -1
        for process_id in range(1,6):
            thread = threading.Thread(target=single_agent, args=(process_id, model, data_dict[code_name], max_attempts, code_name, role, device_type, os_type))
            threads.append(thread)
            thread.start() 
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    main()