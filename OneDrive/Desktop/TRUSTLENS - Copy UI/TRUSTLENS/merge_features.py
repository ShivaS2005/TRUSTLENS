import pandas as pd

image_df = pd.read_csv("results/image_features.csv")
ocr_df = pd.read_csv("results/ocr_features.csv")

merged = pd.merge(
    image_df,
    ocr_df,
    on=["filename", "label"]
)

merged.to_csv("results/fusion_features.csv", index=False)

print("Fusion completed!")
print(merged.shape)