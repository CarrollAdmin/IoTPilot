import matplotlib.pyplot as plt
import numpy as np

hand_tuned = [280.68, 267.18, 301.62, 253.32, 291.3] 
iotpilot = [425.22, 265.44, 374.22, 318.96, 317.28] 
for i in range(len(hand_tuned)):
    hand_tuned[i] = hand_tuned[i] * 60 / 1000
    iotpilot[i] = iotpilot[i] * 60 / 1000

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
fig, ax = plt.subplots(figsize=(7, 5), dpi=1000)
ax.grid(axis="both", linestyle='dotted', zorder=0)

ax.bar(xticks - 0.5* width, hand_tuned, width=width, label="Hand-tuned", color=color[0], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax.bar(xticks + 0.5* width, iotpilot, width=width, label="IoTPilot", color=color[1], alpha=1, zorder=15, linewidth=1, edgecolor='black')
plt.ylabel('Energy (J)', fontsize=20)

plt.xticks(fontsize=22)
plt.yticks(fontsize=22)
plt.legend(loc='upper center', ncol=2, fontsize=22, bbox_to_anchor=(0.5, 1.25), frameon=False, handletextpad=0.01)
ax.set_xticks(xticks, datasets, rotation=45, fontsize=22, ha='right')

plt.grid(True, alpha=0.7)

plt.tight_layout() 
plt.savefig('energy.pdf')
