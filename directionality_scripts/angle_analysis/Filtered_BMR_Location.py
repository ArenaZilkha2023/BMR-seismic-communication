import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# --------------------------------------------------
# 0. PATHS
# --------------------------------------------------

PARENT_DIR = (
    r"X:\Users\Members\George\Projects\BMR_Geo"
    r"\AllOverAgain\Python"
)

AMP_XLSX_PATH = os.path.join(
    PARENT_DIR,
    "BMR_seismic_amplitudes.xlsx"
)

COORD_PATH = os.path.join(
    PARENT_DIR,
    "XYpy.csv"
)

# All PNG, PDF, and Excel outputs will be saved here
OUTPUT_DIR = os.path.join(
    PARENT_DIR,
    "BMR Location",
    "Filtered location"
)

FILTERED_XLSX_PATH = os.path.join(
    OUTPUT_DIR,
    "BMR_seismic_amplitudes_Cage_Filtered.xlsx"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------
# 1. CAGE SETTINGS
# --------------------------------------------------

# Cage corners:
# (-25, -25), (-25, 26), (24, -25), (24, 26)
CAGE_X_MIN = -25
CAGE_X_MAX = 24
CAGE_Y_MIN = -25
CAGE_Y_MAX = 26

# Error buffer in cm
ERROR_BUFFER_CM = 10

# Cage plus error buffer
BUFFER_X_MIN = CAGE_X_MIN - ERROR_BUFFER_CM
BUFFER_X_MAX = CAGE_X_MAX + ERROR_BUFFER_CM
BUFFER_Y_MIN = CAGE_Y_MIN - ERROR_BUFFER_CM
BUFFER_Y_MAX = CAGE_Y_MAX + ERROR_BUFFER_CM

# --------------------------------------------------
# 2. LOAD GEOPHONE COORDINATES
# --------------------------------------------------

# XYpy (1).csv contains two columns and has no header:
# column 1 = X, column 2 = Y
coord_df = pd.read_csv(
    COORD_PATH,
    header=None
)

coord_df = coord_df.iloc[:, :2].copy()
coord_df.columns = ["X", "Y"]

coord_df["X"] = pd.to_numeric(
    coord_df["X"],
    errors="coerce"
)

coord_df["Y"] = pd.to_numeric(
    coord_df["Y"],
    errors="coerce"
)

coord_df = coord_df.dropna(
    subset=["X", "Y"]
).reset_index(drop=True)

# Assign geophone numbers based on row order
coord_df["Mic"] = range(
    1,
    len(coord_df) + 1
 )

# --------------------------------------------------
# 3. READ ALL SHEETS
# --------------------------------------------------

excel_file = pd.ExcelFile(AMP_XLSX_PATH)
sheet_names = excel_file.sheet_names

print(f"Found {len(sheet_names)} sheets:")
print(sheet_names)

# Store the original sheet names and filtered data
filtered_sheets = {}

# --------------------------------------------------
# 4. FILTER EACH SHEET
# --------------------------------------------------

for sheet_name in sheet_names:

    print(f"\nProcessing sheet: {sheet_name}")

    calls_df = pd.read_excel(
        AMP_XLSX_PATH,
        sheet_name=sheet_name
    )

    # Find X BMR and Y BMR robustly
    column_lookup = {
        str(column).strip().lower(): column
        for column in calls_df.columns
    }

    x_bmr_column = column_lookup.get("x bmr")
    y_bmr_column = column_lookup.get("y bmr")

    if x_bmr_column is None or y_bmr_column is None:
        print(
            f"Skipping {sheet_name}: "
            "X BMR and/or Y BMR column was not found."
        )
        continue

    # Convert coordinates only for filtering and plotting
    x_bmr = pd.to_numeric(
        calls_df[x_bmr_column],
        errors="coerce"
    )

    y_bmr = pd.to_numeric(
        calls_df[y_bmr_column],
        errors="coerce"
    )

    # Retain calls inside the cage plus the 10 cm buffer
    retained_mask = (
        x_bmr.between(
            BUFFER_X_MIN,
            BUFFER_X_MAX,
            inclusive="both"
        )
        &
        y_bmr.between(
            BUFFER_Y_MIN,
            BUFFER_Y_MAX,
            inclusive="both"
        )
    )

    filtered_df = calls_df.loc[retained_mask].copy()

    filtered_sheets[sheet_name] = filtered_df

    total_calls = len(calls_df)
    retained_calls = len(filtered_df)
    removed_calls = total_calls - retained_calls

    print(f"Total calls: {total_calls}")
    print(f"Retained calls: {retained_calls}")
    print(f"Removed calls: {removed_calls}")

    # --------------------------------------------------
    # 5. POSITIONS FOR THE MAP
    # --------------------------------------------------

    retained_positions = pd.DataFrame({
        "X BMR": x_bmr.loc[retained_mask],
        "Y BMR": y_bmr.loc[retained_mask]
    }).dropna()

    # --------------------------------------------------
    # 6. CREATE MAP
    # --------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(11, 9)
    )

    # Transparent dashed error-buffer area
    buffer_patch = Rectangle(
        (
            BUFFER_X_MIN,
            BUFFER_Y_MIN
        ),
        BUFFER_X_MAX - BUFFER_X_MIN,
        BUFFER_Y_MAX - BUFFER_Y_MIN,
        facecolor="lightcoral",
        edgecolor="red",
        linestyle="--",
        linewidth=1.8,
        alpha=0.14,
        label="10 cm error buffer",
        zorder=1
    )

    ax.add_patch(buffer_patch)

    # Bold red cage boundary
    cage_patch = Rectangle(
        (
            CAGE_X_MIN,
            CAGE_Y_MIN
        ),
        CAGE_X_MAX - CAGE_X_MIN,
        CAGE_Y_MAX - CAGE_Y_MIN,
        facecolor="none",
        edgecolor="red",
        linestyle="-",
        linewidth=3,
        label="Cage boundary",
        zorder=2
    )

    ax.add_patch(cage_patch)

    # Retained BMR calls
    if not retained_positions.empty:
        ax.scatter(
            retained_positions["X BMR"],
            retained_positions["Y BMR"],
            s=24,
            color="black",
            alpha=0.70,
            edgecolors="none",
            label=(
                f"Retained BMR calls "
                f"(n = {len(retained_positions)})"
            ),
            zorder=4
        )

    # All geophones
    ax.scatter(
        coord_df["X"],
        coord_df["Y"],
        s=58,
        facecolors="white",
        edgecolors="black",
        linewidths=0.9,
        label=f"Geophones (n = {len(coord_df)})",
        zorder=5
    )

    # Geophone numbers
    # for _, geophone in coord_df.iterrows():
    #     ax.text(
    #         geophone["X"],
    #         geophone["Y"],
    #         str(int(geophone["Mic"])),
    #         fontsize=6.5,
    #         color="black",
    #         ha="center",
    #         va="center",
    #         zorder=6
    #     )

    # Dotted horizontal line at y = 0
    ax.axhline(
        y=0,
        color="black",
        linestyle=":",
        linewidth=1.2,
        zorder=3
    )

    # # Stimulus marker
    # ax.scatter(
    #     0,
    #     0,
    #     marker="*",
    #     s=230,
    #     color="yellow",
    #     edgecolors="black",
    #     linewidths=0.9,
    #     label="Stimulus (0, 0)",
    #     zorder=7
    # )

    # --------------------------------------------------
    # 7. PLOT LIMITS
    # --------------------------------------------------

    x_values = list(coord_df["X"])
    y_values = list(coord_df["Y"])

    x_values.extend([
        BUFFER_X_MIN,
        BUFFER_X_MAX
    ])

    y_values.extend([
        BUFFER_Y_MIN,
        BUFFER_Y_MAX
    ])

    if not retained_positions.empty:
        x_values.extend(
            retained_positions["X BMR"].tolist()
        )
        y_values.extend(
            retained_positions["Y BMR"].tolist()
        )

    x_min = min(x_values)
    x_max = max(x_values)
    y_min = min(y_values)
    y_max = max(y_values)

    x_range = max(x_max - x_min, 1)
    y_range = max(y_max - y_min, 1)

    ax.set_xlim(
        x_min - 0.08 * x_range,
        x_max + 0.08 * x_range
    )

    ax.set_ylim(
        y_min - 0.08 * y_range,
        y_max + 0.14 * y_range
    )

    # --------------------------------------------------
    # 8. NORTH INDICATOR
    # --------------------------------------------------

    north_x = x_min + 0.08 * x_range
    north_y = y_min + 0.08 * y_range

    ax.annotate(
        "North",
        xy=(
            north_x,
            north_y + 0.14 * y_range
        ),
        xytext=(
            north_x,
            north_y
        ),
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        arrowprops={
            "arrowstyle": "-|>",
            "color": "black",
            "linewidth": 1.6
        },
        zorder=8
    )

    # --------------------------------------------------
    # 9. PLOT FORMATTING
    # --------------------------------------------------

    ax.set_title(
        f"{sheet_name}: Geophones and Cage-Filtered BMR Calls",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_xlabel("X coordinate")
    ax.set_ylabel("Y coordinate")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(False)

    # Legend outside the plot
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        borderaxespad=0,
        frameon=True
    )

    # Removed-call count underneath the plot
    fig.text(
        0.50,
        0.025,
        (
            "Calls removed outside the cage + 10 cm error buffer "
            f"(or with missing coordinates): {removed_calls}"
        ),
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
        color="darkred"
    )

    # Make room for outside legend and bottom text
    fig.subplots_adjust(
        right=0.72,
        bottom=0.13,
        top=0.92
    )

    # Safe Windows filename
    safe_sheet_name = re.sub(
        r'[\\/:*?"<>|]+',
        "_",
        str(sheet_name)
    )

    png_path = os.path.join(
        OUTPUT_DIR,
        f"{safe_sheet_name}_Cage_Filtered_BMR_Map.png"
    )

    pdf_path = os.path.join(
        OUTPUT_DIR,
        f"{safe_sheet_name}_Cage_Filtered_BMR_Map.pdf"
    )

    fig.savefig(
        png_path,
        dpi=300,
        bbox_inches="tight"
    )

    fig.savefig(
        pdf_path,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"Saved PNG: {png_path}")
    print(f"Saved PDF: {pdf_path}")

# --------------------------------------------------
# 10. SAVE FILTERED EXCEL WORKBOOK
# --------------------------------------------------

with pd.ExcelWriter(
    FILTERED_XLSX_PATH,
    engine="openpyxl"
) as writer:

    for sheet_name, filtered_df in filtered_sheets.items():

        # Excel sheet names have a maximum length of 31 characters
        output_sheet_name = str(sheet_name)[:31]

        filtered_df.to_excel(
            writer,
            sheet_name=output_sheet_name,
            index=False
        )

print("\nFinished.")
print("All maps and the filtered Excel file were saved in:")
print(OUTPUT_DIR)
print("\nFiltered Excel workbook:")
print(FILTERED_XLSX_PATH)