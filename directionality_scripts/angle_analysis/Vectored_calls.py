import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# 1. CONFIGURATION -- EDIT THESE FOR EACH RUN
# --------------------------------------------------
#change the path manually and file name using Spacing label with the correct spacing interval to get the right calls.
ANIMAL = "R4"          # "R4", "R5", or "R6"
CONDITION = "S1"       # "S1" or "S2"
SPACING_LABEL = "0.5_sec"   # matches Detailed_Per_Call_Angles_{SPACING_LABEL}.xlsx
CALL_INDICES = [3, 196, 215  ]   # up to 3 call indices, e.g. [172, 45, 90]


DETAILED_FOLDER = (
    r"X:\Users\Members\George\Projects\BMR_Geo\AllOverAgain\Python\Angle analysis\Results"
)

DETAILED_FILE = os.path.join(
    DETAILED_FOLDER,
    SPACING_LABEL.replace("_", " "),
    f"Detailed_Per_Call_Angles_{SPACING_LABEL}.xlsx"
)

GEOPHONE_FILE = (
    r"X:\Users\Members\George\Projects\BMR_Geo"
    r"\AllOverAgain\Python\XYpy.csv"
)

OUTPUT_FOLDER = (
    r"X:\Users\Members\George\Projects\BMR_Geo\AllOverAgain\Python"
    r"\Angle analysis\Individual vectored calls"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

INTRUDER_LOCATIONS = {
    "S1": (0.0, 120.0),
    "S2": (0.0, -120.0),
}

# Axes are NOT flipped here -- X stays horizontal, Y stays vertical.
HORIZ_LIM = (-55, 55)
VERT_LIM = (-90, 90)
HORIZ_TICKS = np.arange(-40, 41, 20)
VERT_TICKS = np.arange(-75, 76, 25)

CALL_COLORS = ["#830808"]  # up to 3 distinct colors

if len(CALL_INDICES) > 3:
    raise ValueError("A maximum of 3 call indices can be plotted at once.")


detailed_df = pd.read_excel(DETAILED_FILE, sheet_name="Per_Call_Angles")

animal_mask = detailed_df["Animal"].astype(str).str.contains(
    ANIMAL, case=False, na=False
)
condition_mask = detailed_df["Condition"].astype(str).str.contains(
    CONDITION, case=False, na=False
)

subset_df = detailed_df[animal_mask & condition_mask].copy()

if subset_df.empty:
    raise ValueError(
        f"No rows found for Animal='{ANIMAL}', Condition='{CONDITION}'."
    )

geo_raw = pd.read_csv(GEOPHONE_FILE, header=None).to_numpy(dtype=float)
geo_raw = geo_raw[np.all(np.isfinite(geo_raw), axis=1)]

geo_x = geo_raw[:, 0]   # X -> horizontal (no flip)
geo_y = geo_raw[:, 1]   # Y -> vertical (no flip)

cage_x = [-25, -25, 24, 24, -25]
cage_y = [-25, 26, 26, -25, -25]

intruder_x, intruder_y = INTRUDER_LOCATIONS[CONDITION.upper()]

##plots

fig, ax = plt.subplots(figsize=(9, 7))

ax.scatter(
    geo_x, geo_y,
    s=30, c="k", marker="o", label="Geophones", zorder=3
)
ax.plot(cage_x, cage_y, "r-", linewidth=2, label="Cage", zorder=2)
ax.scatter(
    [intruder_x], [intruder_y],
    s=180, c="gray", marker="D",
    edgecolor="black", linewidth=1.2,
    label="Intruder", zorder=4
)
used_calls = []

for i, call_index in enumerate(CALL_INDICES):
    call_row = subset_df[
        pd.to_numeric(subset_df["Call_Index"], errors="coerce") == call_index
    ]

    if call_row.empty:
        print(f"WARNING: Call_Index={call_index} not found for {ANIMAL}{CONDITION}. Skipped.")
        continue

    row = call_row.iloc[0]
    color = CALL_COLORS[i % len(CALL_COLORS)]

    bmr_x, bmr_y = row["BMR_X"], row["BMR_Y"]
    beam_x, beam_y = row["Beam_Max_X"], row["Beam_Max_Y"]
    rel_angle = row["Intruder_Relative_Angle_deg"]

    # BMR location 
    ax.scatter(
        [bmr_x], [bmr_y],
        s=220, c=color, marker="*",
        edgecolor="black", linewidth=0.8,
        zorder=6
    )

    # Beam maximum (X)
    ax.scatter(
        [beam_x], [beam_y],
        s=120, c=color, marker="x",
        linewidth=2.5,
        zorder=6
    )

    # Vector BMR -> beam maximum
    ax.annotate(
        "",
        xy=(beam_x, beam_y),
        xytext=(bmr_x, bmr_y),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=2,
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=5
    )

    used_calls.append((call_index, color, rel_angle))


# Legend 
for call_index, color, rel_angle in used_calls:
    ax.plot(
        [], [], color=color, marker="*", linestyle="None",
        markersize=12, markeredgecolor="black",
        label=f"Call {call_index} ({rel_angle:.1f}°)"
    )
ax.set_xlim(HORIZ_LIM)
ax.set_ylim(VERT_LIM)
ax.set_xticks(HORIZ_TICKS)
ax.set_yticks(VERT_TICKS)
ax.set_aspect("equal")

ax.set_xlabel("X position (cm)", fontsize=12)
ax.set_ylabel("Y position (cm)", fontsize=12)
ax.set_title(
    f"{ANIMAL} {CONDITION} — Beam Vector(s) ({SPACING_LABEL.replace('_', ' ')})",
    fontsize=13, fontweight="bold"
)

ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.0), fontsize=9)
ax.grid(alpha=0.2)

plt.tight_layout()

call_index_str = "-".join(str(c) for c, _, _ in used_calls)
output_filename = f"{ANIMAL}_{CONDITION}_{SPACING_LABEL}_{call_index_str}.pdf"
output_path = os.path.join(OUTPUT_FOLDER, output_filename)

plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved: {output_path}")