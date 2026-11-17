import os
import easyocr

reader = easyocr.Reader(['en'])

INPUT_FOLDERS = [
    ("dataset/Real", "real"),
    ("dataset/Fake", "fake")
]

OUTPUT_FOLDER = "results/ocr"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for folder, label in INPUT_FOLDERS:

    print(f"\nProcessing {label} images...")

    for img_name in os.listdir(folder):

        if img_name.lower().endswith((".png", ".jpg", ".jpeg")):

            img_path = os.path.join(folder, img_name)

            try:
                result = reader.readtext(img_path, detail=0)

                output_file = os.path.join(
                    OUTPUT_FOLDER,
                    os.path.splitext(img_name)[0] + ".txt"
                )

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(result))

                print(f"Saved: {output_file}")

            except Exception as e:
                print(f"Error processing {img_name}: {e}")

print("\nOCR extraction completed successfully!")