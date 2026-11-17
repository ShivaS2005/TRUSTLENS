import os

for root, dirs, files in os.walk("temp_extract"):
    print("\nFolder:", root)
    for file in files:
        print("   ", file)