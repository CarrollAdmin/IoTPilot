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

Native = [sum(RIOT_MQTT_native)/len(RIOT_MQTT_native), sum(RIOT_MMA_native)/len(RIOT_MMA_native), sum(RIOT_IRQ_native)/len(RIOT_IRQ_native), sum(RIOT_UDP_native)/len(RIOT_UDP_native), sum(RIOT_COAP_native)/len(RIOT_COAP_native)]
Context = [sum(RIOT_MQTT_Context)*3/len(RIOT_MQTT_Context), sum(RIOT_MMA_Context)*3/len(RIOT_MMA_Context), sum(RIOT_IRQ_Context)*3/len(RIOT_IRQ_Context), sum(RIOT_UDP_Context)*3/len(RIOT_UDP_Context), sum(RIOT_COAP_Context)*3/len(RIOT_COAP_Context)]
Execution = [sum(RIOT_MQTT_execution)*5/len(RIOT_MQTT_execution), sum(RIOT_MMA_execution)*5/len(RIOT_MMA_execution), sum(RIOT_IRQ_execution)*5/len(RIOT_IRQ_execution), sum(RIOT_UDP_execution)*5/len(RIOT_UDP_execution), sum(RIOT_COAP_execution)*5/len(RIOT_COAP_execution)]

datasets = [
"COAP",
"UDP",
"MQTT",
"MQTT_SN",
"MMA"
]
color = ["#B2182B", "#2166AC", "#92C5DE", "#F4A582"]
xticks = np.arange(len(datasets))
width = 0.18

plt.rcParams['pdf.fonttype'] = 42 
fig, ax = plt.subplots(figsize=(7, 6), dpi=1000)
ax.grid(axis="both", linestyle='dotted', zorder=0)

ax.bar(xticks - 1* width, Native, width=width, label="MapCoder", color=color[0], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks + 1* width, Execution, width=width, label="IoTPilot w. Context and SFG", color=color[2], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks + 0 * width, Context, width=width, label="IoTPilot w. Context", color=color[1], alpha=1, zorder=15, linewidth=1, edgecolor='black')
plt.text(0.35, max(Native) + 12, '*Set max self-debug \n iterations to 10', fontsize=22, style='italic')

plt.ylabel('The number of calls', fontsize=20)

plt.xticks(fontsize=22)
plt.yticks(fontsize=22)
plt.legend(loc='upper center', ncol=2, fontsize=22, bbox_to_anchor=(0.5, 1.45), frameon=False, handletextpad=0.01, columnspacing=-8.5)
ax.set_xticks(xticks, datasets, rotation=45, fontsize=22, ha='right')

plt.grid(True, alpha=0.7)

plt.tight_layout() 
plt.savefig('overhead_call.pdf')
