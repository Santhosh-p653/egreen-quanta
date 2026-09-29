"""
upload_dataset.py — run this in a Colab cell to upload a .npz dataset
file and save it into data/<original_filename>.npz

Usage in Colab:
    %run upload_dataset.py
or just paste the contents of main() into a cell directly.
"""

import os
from google.colab import files


def upload_to_data_folder():
    os.makedirs("data", exist_ok=True)

    uploaded = files.upload()  # opens a file picker in Colab

    for filename, content in uploaded.items():
        if not filename.lower().endswith(".npz"):
            print(f"Skipping '{filename}' — not a .npz file")
            continue
        dest = os.path.join("data", filename)
        with open(dest, "wb") as f:
            f.write(content)
        print(f"Saved to {dest}")


if __name__ == "__main__":
    upload_to_data_folder()
