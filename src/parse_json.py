import json
import matplotlib.pyplot as plt
import numpy as np

# Example data
data = [7, 8, 5, 6, 9, 10, 6, 7, 8, 9, 10, 11, 12, 13, 14]

# Create the box plot
plt.boxplot(data, vert=True, patch_artist=True, showmeans=True)

# Add labels and title
plt.title("Whisker Plot (Box Plot) Example")
plt.ylabel("Values")

# Show the plot
plt.show()

def load_benchmarks_json(path_to_file: str) -> dict:
    with open(path_to_file, "r") as in_file_obj:
        text = in_file_obj.read()
        # convert the text into a dictionary
        return json.loads(text)


if __name__ == "__main__":
    path_to_file = "data/json/0007_small_img.json"
    data = load_benchmarks_json(path_to_file)
    machine_info = data["machine_info"]["cpu"]
    for benchmark in range(len(data["benchmarks"])):
        print(data["benchmarks"][benchmark]["group"])
        print(data["benchmarks"][benchmark]["name"])
        print(data["benchmarks"][benchmark]["stats"])
        print(
            data["benchmarks"][benchmark]["extra_info"]["compression_ratio"]
            if "compression_ratio" in data["benchmarks"][benchmark]["extra_info"]
            else None
        )
