import json

def main():

    # program_names = [
    #     "FreeRTOS_MQTT",
    #     "FreeRTOS_MMA",
    #     "FreeRTOS_COAP",
    #     "FreeRTOS_UDP",
    #     "FreeRTOS_FLASH",
    # ]   
    
    # program_names = [  
    #     "Contiki_DHT11",
    #     "Contiki_led",
    #     "Contiki_UDP",
    #     "Contiki_COAP",
    #     "Contiki_MQTT",
    # ]
    
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
    #     "RIOT_MQTT_SN",
    #     "Zephyr_IRQ",
    #     "RIOT_RTC",
    #     "Zephyr_UDP",
    #     "RIOT_Thread",
    #     "RIOT_Timer",
    #     "RIOT_Flash",
    #     "Zephyr_MMA",
    #     "RIOT_Event",
    #     "RIOT_DHT11",
    #     "RIOT_Warn",
    #     "RIOT_Sched",
    #     "RIOT_MBOX"
    # ]

    iters = 5
    method_type = "deepseeker-coder"

    for program_name in program_names:
        res = ""

        for dir in range(1, iters + 1):
            final_file = "-1_state.json"
            file_path = '../output/'+str(program_name)+'/'+str(dir)+'/'+str(method_type)+'/'+final_file

            try:
                with open(file_path, 'r') as file:
                    file_content = json.load(file)
            except FileNotFoundError:
                print(f"File not found: {file_path}")
                continue  

            ispass = file_content["errorstate"]

            if ispass == "pass":
                res += '1'
            elif ispass == "not pass":
                res += '0'
            else:
                print("invalid")

        print(f"{program_name} | method: {method_type} | res: {res}")

if __name__ == "__main__":
    main()
