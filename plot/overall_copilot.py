import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

datasets = [
"COAP",
"DHT11",
"Event",
"Flash",
"IRQ",
"MBOX",
"MMA",
"MQTT",
"MQTT_SN",
"RTC",
"Sched",
"Thread",
"Timer",
"UDP",
"Warn",
"average"
]

direct =[
"000000000000000",
"000000000000001",
"000001100000001",
"000010101001001",
"110010101010001",
"000000000000000",
"000000000000000",
"000000000000000",
"000000000000000",
"010000100000000",
"000000000000000",
"000000100000000",
"100000111001100",
"000001000000000",
"000100010000000"
]

direct_rate = []  
for binary_string in direct:
    count_of_ones = binary_string.count('1') 
    total_length = len(binary_string)        
    proportion_of_ones = count_of_ones / total_length  
    direct_rate.append(proportion_of_ones)  
direct_rate.append(sum(direct_rate)/len(direct_rate)) 

autocot =[
"000000000000000",
"001001001100000",
"000000000000001",
"000100000000000",
"000001000000000",
"001000000000000",
"000000001001000",
"111100011111101",
"000000010000000",
"011111111111111",
"000000000000000",
"100010100001001",
"000000000001000",
"110110011010111",
"000001000000000"
]


autocot_rate = []  
for binary_string in autocot:
    count_of_ones = binary_string.count('1') 
    total_length = len(binary_string)        
    proportion_of_ones = count_of_ones / total_length  
    autocot_rate.append(proportion_of_ones)  
autocot_rate.append(sum(autocot_rate)/len(autocot_rate)) 

color = ["#B2182B", "#2166AC", "#92C5DE", "#F4A582"] 
xticks = np.arange(len(datasets))
width = 0.3

plt.rcParams['pdf.fonttype'] = 42 
fig, ax = plt.subplots(figsize=(20, 5), dpi=1000)
ax.grid(axis="both", linestyle='dotted', zorder=0)

ax.bar(xticks - 2* width, direct_rate, width=width, label="Direct", color=color[0], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks - 1 * width, autocot_rate, width=width, label="Copilot", color=color[1], alpha=1, zorder=15, linewidth=1, edgecolor='black')
for i in range(len(datasets)):
    for j, rate in enumerate([direct_rate[i], autocot_rate[i]]):
        if rate == 0:
            ax.text(
                xticks[i] + (j - 2) * width, 0, 'X', 
                color=color[0], 
                fontsize=12,  
                fontweight='bold',  
                ha='center', 
                va='bottom', 
                zorder=20
            )


ax.set_ylabel("pass rate", fontsize=30)
plt.legend(loc='upper center', ncol=5, fontsize=30, bbox_to_anchor=(0.5, 1.20), frameon=False, handletextpad=0.5)
ax.set_ylim([0, 1.05])
ax.yaxis.set_major_locator(MultipleLocator(0.2)) 
ax.yaxis.set_tick_params(labelsize=30)
ax.set_xticks(xticks, datasets, rotation=45, fontsize=30, ha='right')

# ax.set_xticks([])
# plt.tick_params(labelsize=35)

plt.show()
plt.savefig("copilot.pdf", bbox_inches='tight')
plt.close()