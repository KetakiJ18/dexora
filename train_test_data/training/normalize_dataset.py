import pandas as pd
import numpy as np

data = pd.read_csv("dataset\\asl_landmarks.csv", header=None)

columns = ["label"]
for i in range(21):
    columns += [f"x{i}", f"y{i}", f"z{i}"]

data.columns = columns


normalized_rows = []

for _, row in data.iterrows():

    label = row["label"]

    coords = row.drop("label").values.reshape(21, 3)

    wrist = coords[0]

    coords = coords - wrist

    max_value = np.max(np.abs(coords))

    if max_value != 0:
        coords = coords / max_value

    coords = coords.flatten()

    normalized_rows.append([label] + coords.tolist())


normalized_df = pd.DataFrame(normalized_rows)

normalized_df.to_csv("dataset\\asl_landmarks_normalized.csv", index=False, header=False)

print("Normalized dataset saved")