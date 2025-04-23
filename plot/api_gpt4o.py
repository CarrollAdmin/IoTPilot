import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

datasets = [
"COAP",
"UDP",
"MQTT",
"MQTT_SN",
"MMA"
]

w = [
    3,
    3,
    6,
    3,
    2
]

direct =[
"110020000000000",
"002011102113011",
"000000000000000",
"113212222222212",
"222222222220222"
]

direct_rate = []  
i = 0
for s in direct:
    sum_of_digits = sum(int(char) for char in s)
    max_digit = w[i]
    i += 1
    if max_digit == 0:
        result = 0
    else:
        result = sum_of_digits / (max_digit * len(s))
    
    direct_rate.append(result)

autocot =[
"232222222322322",
"100102112001011",
"000060060000606",
"012233233202221",
"222211221122212"
]

i = 0
autocot_rate = []  
for s in autocot:
    sum_of_digits = sum(int(char) for char in s)
    max_digit = w[i]
    i += 1
    
    if max_digit == 0:
        result = 0
    else:
        result = sum_of_digits / (max_digit * len(s))
    
    autocot_rate.append(result)

MapCoder =[
"333333333333233",
"111231222122111",
"000600466600000",
"323322332332333",
"222222222222222"

]

i = 0
MapCoder_rate = []  
for s in MapCoder:
    sum_of_digits = sum(int(char) for char in s)
    max_digit = w[i]
    i += 1
    
    if max_digit == 0:
        result = 0
    else:
        result = sum_of_digits / (max_digit * len(s))
    
    MapCoder_rate.append(result)

IoTPilot =[
"233333333333333",
"120211321221222",
"666666666666464",
"333333333333333",
"222222222222222"
]

i = 0
IoTPilot_rate = []  
for s in IoTPilot:
    sum_of_digits = sum(int(char) for char in s)
    max_digit = w[i]
    i += 1
    
    if max_digit == 0:
        result = 0
    else:
        result = sum_of_digits / (max_digit * len(s))
    
    IoTPilot_rate.append(result)

color = ["#B2182B", "#2166AC", "#92C5DE", "#F4A582"] 
xticks = np.arange(len(datasets))
width = 0.18

plt.rcParams['pdf.fonttype'] = 42 
fig, ax = plt.subplots(figsize=(7, 4), dpi=1000)
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


ax.set_ylabel("acc@api", fontsize=30)
plt.legend(loc='upper center', ncol=2, fontsize=25, bbox_to_anchor=(0.5, 1.38), frameon=False, handletextpad=0.1)
ax.set_ylim([0, 1.05])
ax.yaxis.set_major_locator(MultipleLocator(0.2)) 
ax.yaxis.set_tick_params(labelsize=30)
ax.set_xticks(xticks, datasets, rotation=45, fontsize=25, ha='right')

# ax.set_xticks([])
# plt.tick_params(labelsize=35)

plt.show()
plt.savefig("api_gpt4.pdf", bbox_inches='tight')
plt.close()