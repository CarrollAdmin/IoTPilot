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

w = [
    2,
    2,
    2,
    1,
    2
]

Lingma =[
"111111111111111",
"001000000000000",
"111111111111111",
"111111111111111",
"000000000000000"
]

Lingma_rate = []  
i = 0
for s in Lingma:
    sum_of_digits = sum(int(char) for char in s)
    max_digit = w[i]
    i += 1
    if max_digit == 0:
        result = 0
    else:
        result = sum_of_digits / (max_digit * len(s))
    
    Lingma_rate.append(result)
Lingma_rate.append(sum(Lingma_rate)/len(Lingma_rate))

cursor =[
"000110100101101",
"000000000000000",
"111111111111111",
"111111111111111",
"111011111111111"
]

i = 0
cursor_rate = []  
for s in cursor:
    sum_of_digits = sum(int(char) for char in s)
    max_digit = w[i]
    i += 1
    
    if max_digit == 0:
        result = 0
    else:
        result = sum_of_digits / (max_digit * len(s))
    
    cursor_rate.append(result)
cursor_rate.append(sum(cursor_rate)/len(cursor_rate))

copilot =[
"011100000000000",
"000000000000000",
"111111112112111",
"111111111111111",
"111011111111111"
]

i = 0
copilot_rate = []  
for s in copilot:
    sum_of_digits = sum(int(char) for char in s)
    max_digit = w[i]
    i += 1
    
    if max_digit == 0:
        result = 0
    else:
        result = sum_of_digits / (max_digit * len(s))
    
    copilot_rate.append(result)
copilot_rate.append(sum(copilot_rate)/len(copilot_rate))

IoTPilot =[
"122222222222222",
"212222222122221",
"222222221122211",
"111111111111111",
"222121221222222",
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
IoTPilot_rate.append(sum(IoTPilot_rate)/len(IoTPilot_rate))

color = ["#B2182B", "#2166AC", "#92C5DE", "#F4A582"] 
xticks = np.arange(len(datasets))
width = 0.18

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


ax.set_ylabel("acc@api", fontsize=30)
plt.legend(loc='upper center', ncol=2, fontsize=25, bbox_to_anchor=(0.5, 1.38), frameon=False, handletextpad=0.1)
ax.set_ylim([0, 1.05])
ax.yaxis.set_major_locator(MultipleLocator(0.2)) 
ax.yaxis.set_tick_params(labelsize=30)
ax.set_xticks(xticks, datasets, rotation=45, fontsize=25, ha='right')

# ax.set_xticks([])
# plt.tick_params(labelsize=35)

plt.show()
plt.savefig("header_tool.pdf", bbox_inches='tight')
plt.close()