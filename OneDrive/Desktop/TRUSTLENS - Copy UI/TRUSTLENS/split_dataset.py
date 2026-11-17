import splitfolders

splitfolders.ratio(
    "dataset",
    output="dataset_split",
    seed=42,
    ratio=(0.7, 0.15, 0.15)
)

print("Dataset split completed successfully!")