import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# Hypothetical user names
users = [
    "user1",
    "user2",
    "user3",
    "user4",
    "user5",
    "user6",
    "user7",
    "user8",
    "user9",
    "user10"
]

autocot_rate = [0.3, 0.5, 0.5, 0.3, 0.1, 0.05, 0, 0.1, 0.2, 0]

color = ["#B2182B", "#2166AC", "#92C5DE", "#F4A582"]
xticks = np.arange(len(users))
width = 0.3

# Set a global font size
plt.rcParams.update({'font.size': 18})

plt.rcParams['pdf.fonttype'] = 42
fig, ax1 = plt.subplots(figsize=(10, 5), dpi=1000)
ax1.grid(axis="both", linestyle='dotted', zorder=0)

ax1.bar(xticks, autocot_rate, width=width, label="Rate of code changes", color=color[1], alpha=1, zorder=15, linewidth=1, edgecolor='black')

for i in range(len(users)):
    for j, rate in enumerate([autocot_rate[i]]):
        if rate == 0:
            ax1.text(
                xticks[i], 0, '√',
                color=color[0],
                fontsize=28,
                fontweight='bold',  
                ha='center',
                va='bottom',
                zorder=20
            )

ax1.set_ylabel("Rate of code changes", fontsize=22)
ax1.set_ylim([0, 1.05])
ax1.yaxis.set_major_locator(MultipleLocator(0.2))
ax1.yaxis.set_tick_params(labelsize=18)

ax2 = ax1.twinx()
# Use scatter instead of plot for the number of interactions
ax2.scatter(xticks, autocot_rate, label="Number of Interactions", color=color[0], marker='*', s=500, zorder=10)
ax2.set_ylabel("Number of Interactions", fontsize=22)
ax2.tick_params(axis='y', labelsize=22)
ax2.set_ylim([1, 4])

# Add annotation for the maximum number of interactions
ax2.text(len(users) - 5.8, 2.5, "*(Set max interactions to 3)", 
         fontsize=18, color='black', ha='right', style='italic')

ax1.set_xticks(xticks)
ax1.set_xticklabels(users, rotation=45, fontsize=22, ha='right')

ax1.legend(loc='upper left', fontsize=18, frameon=False, handletextpad=0.5)
ax2.legend(loc='upper right', fontsize=18, frameon=False, handletextpad=0.5)

plt.tight_layout()
plt.show()
plt.savefig("user_study.pdf", bbox_inches='tight')
plt.close()
