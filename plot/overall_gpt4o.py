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
"000010000000000",
"100000000000000",
"000000000000000",
"000000100000000",
"000000000000110",
"000000000000000",
"000000000000000",
"000000000000000",
"000000000000000",
"001000000000000",
"000000000000000",
"000000000000001",
"000000000000000",
"000000000000000",
"001000000000000"
]

autocot_rate = []  
for binary_string in autocot:
    count_of_ones = binary_string.count('1') 
    total_length = len(binary_string)        
    proportion_of_ones = count_of_ones / total_length  
    autocot_rate.append(proportion_of_ones)  
autocot_rate.append(sum(autocot_rate)/len(autocot_rate)) 

MapCoder =[
"000010000010100",
"111110111111011",
"010000100111110",
"001011110101111",
"111111111111111",
"111011100111111",
"000000010010100",
"101001000011001",
"000001001001001",
"111000110111111",
"111001000110011",
"101011111111101",
"010111111111110",
"110001011111111",
"000110010111100"

]

MapCoder_rate = []  
for binary_string in MapCoder:
    count_of_ones = binary_string.count('1') 
    total_length = len(binary_string)        
    proportion_of_ones = count_of_ones / total_length  
    MapCoder_rate.append(proportion_of_ones)   
MapCoder_rate.append(sum(MapCoder_rate)/len(MapCoder_rate)) 

IoTPilot =[
"111111101110100",
"111111011111111",
"010110100011100",
"111111111111111",
"111111111111111",
"111111111111111",
"001011110011100",
"111010111111110",
"101111100110000",
"111101011011101",
"101111111111111",
"100110111101111",
"111111111111111",
"101111101111111",
"010011110001001"
]

IoTPilot_rate = []  
for binary_string in IoTPilot:
    count_of_ones = binary_string.count('1') 
    total_length = len(binary_string)        
    proportion_of_ones = count_of_ones / total_length  
    IoTPilot_rate.append(proportion_of_ones)   
IoTPilot_rate.append(sum(IoTPilot_rate)/len(IoTPilot_rate)) 

color = ["#B2182B", "#2166AC", "#92C5DE", "#F4A582"] 
xticks = np.arange(len(datasets))
width = 0.2

plt.rcParams['pdf.fonttype'] = 42 
fig, ax = plt.subplots(figsize=(20, 5), dpi=1000)
ax.grid(axis="both", linestyle='dotted', zorder=0)

ax.bar(xticks - 2* width, direct_rate, width=width, label="Direct", color=color[0], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks - 1 * width, autocot_rate, width=width, label="Auto-CoT", color=color[1], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks, MapCoder_rate, width=width, label="MapCoder", color=color[2], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks + 1 * width, IoTPilot_rate, width=width, label="Ours", color=color[3], alpha=1, zorder=15, linewidth=1, edgecolor='black')

for i in range(len(datasets)):
    for j, rate in enumerate([direct_rate[i], autocot_rate[i], MapCoder_rate[i], IoTPilot_rate[i]]):
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


ax.set_ylabel("rate@pass", fontsize=30)
plt.legend(loc='upper center', ncol=5, fontsize=30, bbox_to_anchor=(0.5, 1.20), frameon=False, handletextpad=0.5)
ax.set_ylim([0, 1.05])
ax.yaxis.set_major_locator(MultipleLocator(0.2)) 
ax.yaxis.set_tick_params(labelsize=30)
ax.set_xticks(xticks, datasets, rotation=45, fontsize=30, ha='right')

# ax.set_xticks([])
# plt.tick_params(labelsize=35)

plt.show()
plt.savefig("overall_gpt4.pdf", bbox_inches='tight')
plt.close()