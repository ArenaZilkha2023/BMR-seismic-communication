import os
import pandas as pd

# --------------------------------------------------
# 1. FOLDERS AND FILES
# --------------------------------------------------

# Folder containing the filtered, untransposed workbook &  Folder where the spaced workbooks will be saved
INPUT_FOLDER = (
    r"X:\Users\Members\George\Projects\BMR_Geo"
    r"\AllOverAgain\Python\Angle analysis"
)

OUTPUT_FOLDER = (
    r"X:\Users\Members\George\Projects\BMR_Geo\AllOverAgain\Python\Angle analysis\Spaced calls"
)

INPUT_FILE = os.path.join(
    INPUT_FOLDER,
    "BMR_seismic_amplitudes_Cage_Filtered260826.xlsx"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

OUTPUT_FILES = {
        0.5: os.path.join(
        OUTPUT_FOLDER,
        "BMR_seismic_amplitudes_Cage_Filtered260826_Spaced_500msec.xlsx"
    ),

    3: os.path.join(
        OUTPUT_FOLDER,
        "BMR_seismic_amplitudes_Cage_Filtered260826_Spaced_3sec.xlsx"
    )

}


INTERVALS_SECONDS = [0.5,  3]


# --------------------------------------------------
# 4. SPACE CALLS WITHIN EACH CONDITION
# --------------------------------------------------

excel_file = pd.ExcelFile(INPUT_FILE)
results = {interval: [] for interval in INTERVALS_SECONDS}

for interval in INTERVALS_SECONDS:

    print(f"\nCreating {interval}-second spaced workbook...")

    with pd.ExcelWriter(
        OUTPUT_FILES[interval],
        engine="openpyxl"
    ) as writer:

        for sheet_name in excel_file.sheet_names:

            df = pd.read_excel(
                INPUT_FILE,
                sheet_name=sheet_name
            )

            # --------------------------------------------------
            # Assign Call_Index BEFORE any sorting/filtering.
            # This preserves the original row order, so
            # Call_Index N corresponds directly to the Kriging
            # sheet "Call_N" for this condition.
            # --------------------------------------------------
            df.insert(0, "Call_Index", range(1, len(df) + 1))

            # Finds the Call Time column even if its capitalization
            # or surrounding spaces differ.
            time_column = next(
                (
                    column
                    for column in df.columns
                    if str(column).strip().lower() == "call time"
                ),
                None
            )

            if time_column is None:
                raise ValueError(
                    f"Sheet '{sheet_name}' does not contain a 'Call Time' column."
                )

            # Convert timestamps to numeric values.
            working_df = df.copy()
            working_df["_TimeNumeric"] = pd.to_numeric(
                working_df[time_column],
                errors="coerce"
            )

            # Remove calls that have no usable timestamp.
            working_df = working_df.dropna(
                subset=["_TimeNumeric"]
            )

            # Sort chronologically before applying the spacing rule.
            working_df = working_df.sort_values(
                "_TimeNumeric",
                kind="stable"
            )

            # Keep the first call. Keep later calls only when they occur
            # at least `interval` seconds after the previously retained call.
            retained_indices = []
            last_retained_time = None

            for row_index, row in working_df.iterrows():

                current_time = row["_TimeNumeric"]

                if (
                    last_retained_time is None
                    or current_time - last_retained_time >= interval
                ):
                    retained_indices.append(row_index)
                    last_retained_time = current_time

            # Preserve original columns/order, but keep only retained rows.
            # Call_Index travels with each row, so it still points to the
            # correct Kriging Call_N sheet after spacing.
            spaced_df = df.loc[retained_indices].copy()

            # Re-sort output chronologically for readability.
            spaced_df = spaced_df.sort_values(
                time_column,
                kind="stable"
            )

            spaced_df.to_excel(
                writer,
                sheet_name=str(sheet_name)[:31],
                index=False
            )

            results[interval].append(
                {
                    "Condition": sheet_name,
                    "Original calls": len(df),
                    "Retained calls": len(spaced_df),
                    "Removed calls": len(df) - len(spaced_df),
                }
            )

# --------------------------------------------------
# 5. PRINT RESULTS
# --------------------------------------------------

print("\nFinished successfully.")

for interval in INTERVALS_SECONDS:

    print(f"\n{interval}-second spacing:")
    print(f"Saved: {OUTPUT_FILES[interval]}")

    for result in results[interval]:
        print(
            f"  {result['Condition']}: "
            f"{result['Original calls']} → "
            f"{result['Retained calls']} calls retained "
            f"({result['Removed calls']} removed)"
        )

# --------------------------------------------------
# 6. SUMMARY TABLE: BEAMS LOST PER CONDITION
# --------------------------------------------------

all_conditions = excel_file.sheet_names

summary_rows = []

for condition in all_conditions:

    row = {"Condition": condition}

    for interval in INTERVALS_SECONDS:

        match = next(
            (
                r for r in results[interval]
                if r["Condition"] == condition
            ),
            None
        )

        column_label = f"Lost @ {interval}s"
        row[column_label] = match["Removed calls"] if match else None

    summary_rows.append(row)

summary_df = pd.DataFrame(summary_rows)

print("\n--- Beams Lost per Condition ---")
print(summary_df.to_string(index=False))

summary_path = os.path.join(
    OUTPUT_FOLDER,
    "Beams_Lost_Summary.xlsx"
)
summary_df.to_excel(summary_path, index=False)
print(f"\nSummary table saved to:\n{summary_path}")