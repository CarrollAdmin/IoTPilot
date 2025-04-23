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
    3,
    3,
    2,
    2,
    6
]

w_raw =[
"232232222233232",
"122121212111221",
"212211222201122",
"112111111111111",
"100000000050000"
]

w_raw_rate = []  
i = 0
for s in w_raw:
    sum_of_digits = sum(int(char) for char in s)
    max_digit = w[i]
    i += 1
    if max_digit == 0:
        result = 0
    else:
        result = sum_of_digits / (max_digit * len(s))
    
    w_raw_rate.append(result)
w_raw_rate.append(sum(w_raw_rate)/len(w_raw_rate)) 

w_SFG =[
"333333332323333",
"32311333311213",
"222222222222222",
"201202201222022",
"666606660161660"
]

i = 0
w_SFG_rate = []  
for s in w_SFG:
    sum_of_digits = sum(int(char) for char in s)
    max_digit = w[i]
    i += 1
    
    if max_digit == 0:
        result = 0
    else:
        result = sum_of_digits / (max_digit * len(s))
    
    w_SFG_rate.append(result)
w_SFG_rate.append(sum(w_SFG_rate)/len(w_SFG_rate)) 



color = ["#B2182B", "#2166AC", "#92C5DE", "#F4A582"] 
xticks = np.arange(len(datasets))
width = 0.25

plt.rcParams['pdf.fonttype'] = 42 
fig, ax = plt.subplots(figsize=(7, 4), dpi=1000)
ax.grid(axis="both", linestyle='dotted', zorder=0)

ax.bar(xticks - 1* width, w_raw_rate, width=width, label="w. raw code", color=color[0], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks - 0 *width, w_SFG_rate, width=width, label="w. SFG", color=color[1], alpha=1, zorder=15, linewidth=1, edgecolor='black')

for i in range(len(datasets)):
    for j, rate in enumerate([w_raw_rate[i], w_SFG_rate[i]]):
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
plt.legend(loc='upper center', ncol=2, fontsize=25, bbox_to_anchor=(0.5, 1.22), frameon=False, handletextpad=0.1)
ax.set_ylim([0, 1.05])
ax.yaxis.set_major_locator(MultipleLocator(0.2)) 
ax.yaxis.set_tick_params(labelsize=30)
ax.set_xticks(xticks, datasets, rotation=45, fontsize=25, ha='right')

# ax.set_xticks([])
# plt.tick_params(labelsize=35)

plt.show()
plt.savefig("api_sfg.pdf", bbox_inches='tight')
plt.close()