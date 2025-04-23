import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.gridspec as gridspec
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import matplotlib.transforms as mtransforms

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

# autocot_rate = [0.7, 0.6, 0.6, 0.6, 0.05, 0.7, 0.6, 0, 0.1, 0]
# iotpilot_rate = [0.05, 0, 0.05, 0.05, 0.1, 0.05, 0, 0.05, 0, 0]

autocot_rate = [100 + 20 , 60 + 20, 60 + 20, 55 + 20, 65 + 20, 100 + 20, 20 + 60, 60 + 10, 55 + 10, 60 + 10]
iotpilot_rate = [45 + 20, 2 + 20, 40 + 20, 35 + 20, 60 + 20, 35 + 20, 2 + 20, 6 + 10, 2 + 10, 2 + 10] 
print((sum(autocot_rate)/len(autocot_rate) - sum(iotpilot_rate)/len(iotpilot_rate))/(sum(autocot_rate)/len(autocot_rate)))
# user_satisfaction = [5, 5, 3, 3, 5, 4, 5, 5, 4, 5]

color = ["#B2182B", "#2166AC", "#92C5DE", "#F4A582"]
xticks = np.arange(len(users))
width = 0.3

# Set a global font size
plt.rcParams.update({'font.size': 18})

plt.rcParams['pdf.fonttype'] = 42
# Create a figure with GridSpec to create a small area for the annotation axis
fig = plt.figure(figsize=(10, 6), dpi=1000)
gs = gridspec.GridSpec(2, 1, height_ratios=[6, 1], hspace=0.55)  # Reduced hspace to move axes closer
ax1 = fig.add_subplot(gs[0])
ax3 = fig.add_subplot(gs[1])  # Third axis for annotations

ax1.grid(axis="both", linestyle='dotted', zorder=0)

ax1.bar(xticks - 0.5 * width, autocot_rate, width=width, label="MapCoder", color=color[1], alpha=1, zorder=15, linewidth=1, edgecolor='black')
ax1.bar(xticks + 0.5 * width, iotpilot_rate, width=width, label="IoTPilot", color=color[3], alpha=1, zorder=15, linewidth=1, edgecolor='black')

for i in range(len(users)):
    for j, rate in enumerate([autocot_rate[i], iotpilot_rate[i]]):
        if rate == 0:
            ax1.text(
                xticks[i] + (j - 0.3) * width, 0, '✔',
                color=color[0],
                fontsize=28,
                fontweight='bold',  
                ha='center',
                va='bottom',
                zorder=20
            )

ax1.set_ylabel("Time Consumption (min)", fontsize=22)
ax1.set_ylim([0, 125])
ax1.yaxis.set_major_locator(MultipleLocator(20))
ax1.yaxis.set_tick_params(labelsize=18)
ax1.set_xticks(xticks)
ax1.set_xticklabels(users, rotation=45, fontsize=22, ha='right', rotation_mode='anchor')

# Move ax2 creation after ax1 setup
# ax2 = ax1.twinx()
# Use scatter instead of plot for the number of interactions
# ax2.scatter(xticks, user_satisfaction, label="User satisfaction", color=color[0], marker='*', s=500, zorder=10)
# ax2.set_ylabel("Number of Interactions", fontsize=22)
# ax2.tick_params(axis='y', labelsize=22)
# ax2.set_ylim([0, 5.5])
# ax2.yaxis.set_major_locator(MultipleLocator(1))

# Create curly brace for the "familiar" range
def curly_brace(x1, x2, y, height=0.075, width=0.5, pointing='down'):
    # Points in data coordinates
    middle = (x1 + x2) / 2
    width_points = abs(x2 - x1) * width
    
    if pointing == 'up':
        y1, y2 = y, y + height
    else:
        y1, y2 = y, y - height
    
    # The control points for the splines
    cp1x, cp1y = x1, y1
    cp2x, cp2y = x1, y2
    cp3x, cp3y = middle - width_points, y2
    cp4x, cp4y = middle, y1
    cp5x, cp5y = middle + width_points, y2
    cp6x, cp6y = x2, y2
    cp7x, cp7y = x2, y1
    
    verts = [
        (cp1x, cp1y), # P0
        (cp2x, cp2y), # P1
        (cp3x, cp3y), # P2
        (cp4x, cp4y), # P3
        (cp5x, cp5y), # P4
        (cp6x, cp6y), # P5
        (cp7x, cp7y), # P6
    ]
    
    codes = [
        Path.MOVETO,  # P0
        Path.CURVE3,  # P1
        Path.CURVE3,  # P2
        Path.CURVE3,  # P3
        Path.CURVE3,  # P4
        Path.CURVE3,  # P5
        Path.CURVE3,  # P6
    ]
    
    path = Path(verts, codes)
    patch = PathPatch(path, facecolor='none', edgecolor='black', lw=2)
    return patch

# Configure the annotation axis (ax3)
ax3.set_xlim(ax1.get_xlim())
ax3.set_ylim(0, 1)  # Increase the height to make room for the moved-up annotations
ax3.axis('off')  # Hide the axis

# Add curly brace for "familiar" using the same function
brace_y_position_familiar = 0.7 # Increased from 1.0
curly_familiar = curly_brace(xticks[6]+0.05, xticks[9], brace_y_position_familiar, height=0.15, width=0.3, pointing='down')
ax3.add_patch(curly_familiar)
ax3.text(xticks[7]+0.5, brace_y_position_familiar - 0.2, 'experts', ha='center', va='top', fontsize=22, color='black', style='italic')

# Add curly brace for "not familiar" range - placed ABOVE the text
brace_y_position = 0.7  # Increased from 1.0
curly = curly_brace(xticks[0], xticks[6]-0.05, brace_y_position, height=0.15, width=0.3, pointing='down')
ax3.add_patch(curly)
ax3.text(xticks[3], brace_y_position - 0.2, 'non-experts', ha='center', va='top', fontsize=22, color='black', style='italic')

ax1.legend(loc='upper center', ncol=2, fontsize=22, bbox_to_anchor=(0.5, 1.21), frameon=False, handletextpad=0.01)
# ax2.legend(loc='upper right', fontsize=18, frameon=False, handletextpad=0.5, bbox_to_anchor=(1, 1.27))

plt.tight_layout()
plt.show()
plt.savefig("user_study.pdf", bbox_inches='tight')
plt.close()
