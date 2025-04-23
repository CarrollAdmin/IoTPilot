import matplotlib.pyplot as plt
import numpy as np

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
RIOT_MQTT = [sum(RIOT_MQTT_native)/len(RIOT_MQTT_native), sum(RIOT_MQTT_Context)*3/len(RIOT_MQTT_Context), sum(RIOT_MQTT_execution)*5/len(RIOT_MQTT_execution)]  
RIOT_MMA = [sum(RIOT_MMA_native)/len(RIOT_MMA_native), sum(RIOT_MMA_Context)*3/len(RIOT_MMA_Context), sum(RIOT_MMA_execution)*5/len(RIOT_MMA_execution)]  
RIOT_IRQ = [sum(RIOT_IRQ_native)/len(RIOT_IRQ_native), sum(RIOT_IRQ_Context)*3/len(RIOT_IRQ_Context), sum(RIOT_IRQ_execution)*5/len(RIOT_IRQ_execution)]
RIOT_UDP = [sum(RIOT_UDP_native)/len(RIOT_UDP_native), sum(RIOT_UDP_Context)*3/len(RIOT_UDP_Context), sum(RIOT_UDP_execution)*5/len(RIOT_UDP_execution)]
RIOT_COAP = [sum(RIOT_COAP_native)/len(RIOT_COAP_native), sum(RIOT_COAP_Context)*3/len(RIOT_COAP_Context), sum(RIOT_COAP_execution)*5/len(RIOT_COAP_execution)]

plt.figure(figsize=(6, 5), dpi=1000)

plt.plot(labels, RIOT_MQTT, marker='o', linestyle='--', color='b', linewidth=8, markersize=23, label='MQTT')
plt.plot(labels, RIOT_MMA, marker='s', linestyle='--', color='g', linewidth=8, markersize=23, label='MMA')
plt.plot(labels, RIOT_IRQ, marker='^', linestyle='--', color='r', linewidth=8, markersize=23, label='IRQ')
plt.plot(labels, RIOT_UDP, marker='d', linestyle='--', color='c', linewidth=8, markersize=23, label='UDP')
plt.plot(labels, RIOT_COAP, marker='>', linestyle='--', color='m', linewidth=8, markersize=23, label='COAP')


plt.text(0.02, max(RIOT_MQTT) -2, '*Set max self-debug \n iterations to 10', fontsize=20, style='italic')

plt.xlabel('Chains', fontsize=20)
plt.ylabel('The number of calls', fontsize=20)

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.legend(loc='upper center', ncol=3, fontsize=20, bbox_to_anchor=(0.5, 1.30), frameon=False, handletextpad=0.01)

plt.grid(True, alpha=0.7)

plt.tight_layout() 


plt.tight_layout() # Adjust layout to fit all elements properly
plt.savefig('overhead_call.pdf')
