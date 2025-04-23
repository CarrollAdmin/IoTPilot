import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

def calculate_95_confidence_interval(data):
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)
    sem = std_dev / np.sqrt(len(data))
    confidence = 0.95
    degrees_of_freedom = len(data) - 1
    t_score = stats.t.ppf((1 + confidence) / 2, degrees_of_freedom)
    confidence_interval = (mean - t_score * sem, mean + t_score * sem)
    return confidence_interval

def calculate_error(confidence_interval):
    return (confidence_interval[1] - confidence_interval[0]) / 2

# Data
RIOT_MQTT_Context = [3, 3, 11, 4, 3, 11, 9, 2, 5, 3, 11, 4, 4, 8, 4]
RIOT_MMA_Context = [2, 4, 2, 2, 2, 1, 1, 4, 3, 2, 2, 2, 2, 11, 2]
RIOT_IRQ_Context = [6, 2, 2, 4, 4, 3, 1, 11, 5, 2, 3, 5, 1, 1, 1]
RIOT_UDP_Context = [3, 3, 8, 2, 5, 2, 1, 1, 1, 2, 1, 2, 5, 3, 4]
RIOT_COAP_Context = [3, 11, 11, 3, 8, 2, 2, 3, 2, 3, 5, 11, 5, 11, 11]

RIOT_MQTT_native = [7, 2, 5, 7, 5, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11]
RIOT_MMA_native  = [2, 2, 5, 2, 2, 4, 4, 10, 4, 2, 3, 4, 2, 2, 2]
RIOT_IRQ_native  = [1, 1, 1, 1, 1, 11, 11, 11, 11, 11, 11, 11, 1, 1, 1]
RIOT_UDP_native  = [3, 3, 11, 5, 5, 11, 6, 11, 11, 6, 11, 11, 11, 5, 11]
RIOT_COAP_native = [11, 11, 11, 11, 11, 11, 7, 9, 9, 11, 11, 11, 11, 11, 11]

RIOT_MQTT_execution = [4, 11, 2, 7, 6, 4, 3, 5, 5, 4, 8, 1, 1, 7, 11]
RIOT_MMA_execution = [2, 5, 2, 4, 2, 2, 1, 2, 2, 1, 1, 11, 2, 1, 2]
RIOT_IRQ_execution = [4, 6, 11, 2, 2, 2, 1, 2, 2, 2, 2, 7, 6, 2, 4]
RIOT_UDP_execution = [2, 2, 2, 1, 2, 1, 1, 1, 1, 1, 2, 2, 3, 2, 1]
RIOT_COAP_execution = [2, 2, 11, 8, 11, 10, 6, 3, 4, 6, 1, 11, 4, 6, 4]

labels = ['Native', 'w.Context', 'w.SFG']

scaling_factors = {
    "MQTT": [27720, 27720 + 772 + 190 + 172, 27720 + 772 + 190 + 172 + 306 + 245],
    "MMA": [27669, 27669 + 766 + 190 + 172, 27669 + 766 + 190 + 172 + 306 + 245],
    "IRQ": [27589, 27589 + 758 + 190 + 172, 27589 + 758 + 190 + 172 + 306 + 245],
    "UDP": [27604, 27604 + 760 + 190 + 172, 27604 + 760 + 190 + 172 + 306 + 245],
    "COAP": [27683, 27683 + 768 + 190 + 172, 27683 + 768 + 190 + 172 + 306 + 245]
}

RIOT_MQTT = [sum(RIOT_MQTT_native)*scaling_factors["MQTT"][0]/len(RIOT_MQTT_native)/1000,
             sum(RIOT_MQTT_Context)*scaling_factors["MQTT"][1]/len(RIOT_MQTT_Context)/1000,
             sum(RIOT_MQTT_execution)*scaling_factors["MQTT"][2]/len(RIOT_MQTT_execution)/1000]

RIOT_MMA = [sum(RIOT_MMA_native)*scaling_factors["MMA"][0]/len(RIOT_MMA_native)/1000,
            sum(RIOT_MMA_Context)*scaling_factors["MMA"][1]/len(RIOT_MMA_Context)/1000,
            sum(RIOT_MMA_execution)*scaling_factors["MMA"][2]/len(RIOT_MMA_execution)/1000]

RIOT_IRQ = [sum(RIOT_IRQ_native)*scaling_factors["IRQ"][0]/len(RIOT_IRQ_native)/1000,
            sum(RIOT_IRQ_Context)*scaling_factors["IRQ"][1]/len(RIOT_IRQ_Context)/1000,
            sum(RIOT_IRQ_execution)*scaling_factors["IRQ"][2]/len(RIOT_IRQ_execution)/1000]

RIOT_UDP = [sum(RIOT_UDP_native)*scaling_factors["UDP"][0]/len(RIOT_UDP_native)/1000,
            sum(RIOT_UDP_Context)*scaling_factors["UDP"][1]/len(RIOT_UDP_Context)/1000,
            sum(RIOT_UDP_execution)*scaling_factors["UDP"][2]/len(RIOT_UDP_execution)/1000]

RIOT_COAP = [sum(RIOT_COAP_native)*scaling_factors["COAP"][0]/len(RIOT_COAP_native)/1000,
             sum(RIOT_COAP_Context)*scaling_factors["COAP"][1]/len(RIOT_COAP_Context)/1000,
             sum(RIOT_COAP_execution)*scaling_factors["COAP"][2]/len(RIOT_COAP_execution)/1000]

error_MQTT = [calculate_error(calculate_95_confidence_interval(RIOT_MQTT_native))*scaling_factors["MQTT"][0],
              calculate_error(calculate_95_confidence_interval(RIOT_MQTT_Context))*scaling_factors["MQTT"][1],
              calculate_error(calculate_95_confidence_interval(RIOT_MQTT_execution))*scaling_factors["MQTT"][2]]

error_MMA = [calculate_error(calculate_95_confidence_interval(RIOT_MMA_native))*scaling_factors["MMA"][0],
             calculate_error(calculate_95_confidence_interval(RIOT_MMA_Context))*scaling_factors["MMA"][1],
             calculate_error(calculate_95_confidence_interval(RIOT_MMA_execution))*scaling_factors["MMA"][2]]

error_IRQ = [calculate_error(calculate_95_confidence_interval(RIOT_IRQ_native))*scaling_factors["IRQ"][0],
             calculate_error(calculate_95_confidence_interval(RIOT_IRQ_Context))*scaling_factors["IRQ"][1],
             calculate_error(calculate_95_confidence_interval(RIOT_IRQ_execution))*scaling_factors["IRQ"][2]]

error_UDP = [calculate_error(calculate_95_confidence_interval(RIOT_UDP_native))*scaling_factors["UDP"][0],
             calculate_error(calculate_95_confidence_interval(RIOT_UDP_Context))*scaling_factors["UDP"][1],
             calculate_error(calculate_95_confidence_interval(RIOT_UDP_execution))*scaling_factors["UDP"][2]]

error_COAP = [calculate_error(calculate_95_confidence_interval(RIOT_COAP_native))*scaling_factors["COAP"][0],
              calculate_error(calculate_95_confidence_interval(RIOT_COAP_Context))*scaling_factors["COAP"][1],
              calculate_error(calculate_95_confidence_interval(RIOT_COAP_execution))*scaling_factors["COAP"][2]]

plt.figure(figsize=(6, 5), dpi=1000)

plt.plot(labels, RIOT_MQTT, marker='o', linestyle='--', color='b', linewidth=8, markersize=23, label='MQTT')
plt.plot(labels, RIOT_MMA, marker='s', linestyle='--', color='g', linewidth=8, markersize=23, label='MMA')
plt.plot(labels, RIOT_IRQ, marker='^', linestyle='--', color='r', linewidth=8, markersize=23, label='IRQ')
plt.plot(labels, RIOT_UDP, marker='d', linestyle='--', color='c', linewidth=8, markersize=23, label='UDP')
plt.plot(labels, RIOT_COAP, marker='>', linestyle='--', color='m', linewidth=8, markersize=23, label='COAP')

plt.text(0.55, max(RIOT_MQTT) -7, '*Set max self-debug \n iterations to 10', fontsize=20, style='italic')

plt.xlabel('Chains', fontsize=20)
plt.ylabel('Tokens (k)', fontsize=20)

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.legend(loc='upper center', ncol=3, fontsize=20, bbox_to_anchor=(0.5, 1.35), frameon=False, handletextpad=0.01)

plt.grid(True, alpha=0.7)

plt.tight_layout() 

plt.savefig('overhead_token.pdf')
plt.show()
