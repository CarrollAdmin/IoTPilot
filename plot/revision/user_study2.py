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

# User satisfaction scores (scale 1-5)
user_satisfaction = [5, 4, 4, 5, 3, 5, 4, 5, 5, 4]

color = ["#B2182B", "#2166AC", "#92C5DE", "#F4A582"]
xticks = np.arange(len(users))
width = 0.6

# Set a global font size
plt.rcParams.update({'font.size': 18})
plt.rcParams['pdf.fonttype'] = 42

# Create a figure
fig = plt.figure(figsize=(5, 6), dpi=1000)
ax = fig.add_subplot(111)

ax.grid(axis="y", linestyle='dotted', zorder=0)

# Create the bar chart for user satisfaction
ax.bar(xticks, user_satisfaction, width=width, color=color[3], alpha=1, zorder=15, 
       linewidth=1, edgecolor='black')

# Add labels and formatting
ax.set_ylabel("User Satisfaction (1-5)", fontsize=22)
ax.set_ylim([0, 5.5])
ax.yaxis.set_major_locator(MultipleLocator(1))
ax.yaxis.set_tick_params(labelsize=18)
ax.set_xticks(xticks)
ax.set_xticklabels(users, rotation=45, fontsize=22, ha='right', rotation_mode='anchor')

# Add value labels on top of each bar
# for i, satisfaction in enumerate(user_satisfaction):
#     ax.text(xticks[i], satisfaction + 0.1, str(satisfaction), 
#             ha='center', va='bottom', fontsize=18)

plt.tight_layout()
plt.savefig("user_study2.pdf", bbox_inches='tight')
plt.show()
plt.close()
