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
"000000000000000",
"000000000000000",
"100000000000000",
"000000000000000",
"000000000000010",
"000000000000000",
"000000000000000",
"000000000000000",
"111110111011111",
"000000000000000",
"010001010010001",
"000000000000000",
"000000000000000",
"000000000000000"
]

direct_rate = []  
for binary_string in direct:
    count_of_ones = binary_string.count('1') 
    total_length = len(binary_string)        
    proportion_of_ones = count_of_ones / total_length  
    direct_rate.append(proportion_of_ones)  
direct_rate.append(sum(direct_rate)/len(direct_rate)) 

autocot =[
"100000000000000",
"001001001010011",
"000000000000000",
"000000000000000",
"000000000000000",
"000000100111011",
"000000000000000",
"000000000000000",
"000000000000000",
"111111011111111",
"000000000000000",
"100000001000110",
"000000000000000",
"000100000000000",
"111001100001010"
]

autocot_rate = []  
for binary_string in autocot:
    count_of_ones = binary_string.count('1') 
    total_length = len(binary_string)        
    proportion_of_ones = count_of_ones / total_length  
    autocot_rate.append(proportion_of_ones)  
autocot_rate.append(sum(autocot_rate)/len(autocot_rate)) 

MapCoder =[
"001110000000000",
"111110010110100",
"001011000001001",
"111101110001111",
"000000001110001",
"011111111111110",
"111111111111111",
"000000000001000",
"001000000000011",
"111111111111111",
"100111110100111",
"111111011111111",
"111000111111111",
"101001010101101",
"111111111111101"

]

MapCoder_rate = []  
for binary_string in MapCoder:
    count_of_ones = binary_string.count('1') 
    total_length = len(binary_string)        
    proportion_of_ones = count_of_ones / total_length  
    MapCoder_rate.append(proportion_of_ones)   
MapCoder_rate.append(sum(MapCoder_rate)/len(MapCoder_rate)) 

IoTPilot =[
"110100110111101",
"111011101111111",
"111111100111100",
"111110110111100",
"110101011010110",
"110111111111111",
"111111111111111",
"101111011111011",
"110011011101010",
"111111111111111",
"111110100110111",
"111111110111111",
"111111111100111",
"111111111111111",
"111111111111111"
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
                fontsize=15,  
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
plt.savefig("overall_deepseek.pdf", bbox_inches='tight')
plt.close()