import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

datasets = [
"COAP",
"UDP",
"MMA",
"IRQ",
"MQTT",
"Average"
]

Lingma =[
"000000000000000",
"000000000101000",
"000000000000000",
"001000000000000",
"000000000000000"
]

Lingma_rate = []  
for binary_string in Lingma:
    count_of_ones = binary_string.count('1') 
    total_length = len(binary_string)        
    proportion_of_ones = count_of_ones / total_length  
    Lingma_rate.append(proportion_of_ones)   
Lingma_rate.append(sum(Lingma_rate)/len(Lingma_rate)) 

cursor =[
"000000000001001",
"000111111000110",
"000000000000000",
"101000000000001",
"000000000000000"
]

cursor_rate = []  
for cursor_string in cursor:
    count_of_ones = cursor_string.count('1') 
    total_length = len(cursor_string)        
    proportion_of_ones = count_of_ones / total_length  
    cursor_rate.append(proportion_of_ones)  
cursor_rate.append(sum(cursor_rate)/len(cursor_rate)) 

copilot =[
"000000000000000",
"110110011010111",
"000000001001000",
"000000000000000",
"111100011111101"
]

copilot_rate = []  
for binary_string in copilot:
    count_of_ones = binary_string.count('1') 
    total_length = len(binary_string)        
    proportion_of_ones = count_of_ones / total_length  
    copilot_rate.append(proportion_of_ones)  
copilot_rate.append(sum(copilot_rate)/len(copilot_rate)) 


IoTPilot =[
"110100110111101",
"111111111111111",
"111111111111111",
"110101011010110",
"101111011111011"
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
fig, ax = plt.subplots(figsize=(9, 4), dpi=1000)
ax.grid(axis="both", linestyle='dotted', zorder=0)

ax.bar(xticks - 2* width, Lingma_rate, width=width, label="TONGYI Lingma", color=color[0], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks - 1 * width, cursor_rate, width=width, label="Cursor", color=color[1], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks, copilot_rate, width=width, label="Copilot", color=color[2], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks + 1 * width, IoTPilot_rate, width=width, label="IoTPilot", color=color[3], alpha=1, zorder=15, linewidth=1, edgecolor='black')

for i in range(len(datasets)):
    for j, rate in enumerate([Lingma_rate[i], cursor_rate[i], copilot_rate[i], IoTPilot_rate[i]]):
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
plt.legend(loc='upper center', ncol=2, fontsize=22, bbox_to_anchor=(0.5, 1.36), frameon=False, handletextpad=0.1)
ax.set_ylim([0, 1.05])
ax.yaxis.set_major_locator(MultipleLocator(0.2)) 
ax.yaxis.set_tick_params(labelsize=30)
ax.set_xticks(xticks, datasets, rotation=45, fontsize=25, ha='right')


plt.show()
plt.savefig("tool.pdf", bbox_inches='tight')
plt.close()