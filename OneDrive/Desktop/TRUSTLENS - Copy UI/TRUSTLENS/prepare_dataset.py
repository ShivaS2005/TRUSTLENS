import os
import zipfile
import shutil
import fitz

# ----------------------------
# Folder paths
# ----------------------------
ZIP_FOLDER = "zip_files"
TEMP_FOLDER = "temp_extract"
DATASET_FOLDER = "dataset"

REAL_FOLDER = os.path.join(DATASET_FOLDER, "Real")
FAKE_FOLDER = os.path.join(DATASET_FOLDER, "Fake")

# Maximum fake images required
MAX_FAKE = 100

# Create folders
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(REAL_FOLDER, exist_ok=True)
os.makedirs(FAKE_FOLDER, exist_ok=True)

# ----------------------------
# Extract ZIP files
# ----------------------------
print("Extracting ZIP files...")

for file in os.listdir(ZIP_FOLDER):

    if file.endswith(".zip"):

        zip_path = os.path.join(ZIP_FOLDER, file)

        extract_path = os.path.join(
            TEMP_FOLDER,
            os.path.splitext(file)[0]
        )

        os.makedirs(extract_path, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

print("ZIP extraction completed!")

# ----------------------------
# Prepare dataset
# ----------------------------
real_count = 1
fake_count = 1

for root, dirs, files in os.walk(TEMP_FOLDER):

    root_upper = root.upper()

    for file in files:

        filepath = os.path.join(root, file)

        # -------------------------
        # REAL PDFs
        # -------------------------
        if (
            "GPAY SCRN" in root_upper or
            "GPAY SCRN 2" in root_upper or
            "IMG_2410" in root_upper or
            "IMG_2470" in root_upper
        ):

            if file.lower().endswith(".pdf"):

                pdf = fitz.open(filepath)

                print("Converting REAL:", file)

                for page in pdf:

                    pix = page.get_pixmap(dpi=300)

                    save_path = os.path.join(
                        REAL_FOLDER,
                        f"real_{real_count}.png"
                    )

                    pix.save(save_path)

                    real_count += 1

        # -------------------------
        # FAKE PDF (Google Pay)
        # -------------------------
        elif "GPAY SYNTHETIC IMAGES" in root_upper:

            if file.lower().endswith(".pdf"):

                pdf = fitz.open(filepath)

                print("Converting FAKE PDF:", file)

                for page in pdf:

                    if fake_count > MAX_FAKE:
                        break

                    pix = page.get_pixmap(dpi=300)

                    save_path = os.path.join(
                        FAKE_FOLDER,
                        f"fake_{fake_count}.png"
                    )

                    pix.save(save_path)

                    fake_count += 1

        # -------------------------
        # FAKE PNG/JPG
        # -------------------------
        elif file.lower().endswith((".png", ".jpg", ".jpeg")):

            if fake_count > MAX_FAKE:
                continue

            print("Copying:", file)

            save_path = os.path.join(
                FAKE_FOLDER,
                f"fake_{fake_count}.png"
            )

            shutil.copy(filepath, save_path)

            fake_count += 1

print("\n===================================")
print("Dataset preparation completed!")
print("===================================")

print("Real Images :", real_count - 1)
print("Fake Images :", fake_count - 1)