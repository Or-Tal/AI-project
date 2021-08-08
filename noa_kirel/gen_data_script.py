import os

if __name__ == "__main__":
    if not os.path.exists("datasets"):
        os.mkdir("datasets")
    # for i in range(3, 16, 3):
    #     os.system(f"python generate_dataset.py --n {i} --save_path ./datasets/{i}_cities.npy")
    # for i in range(50, 101, 10):
    #     os.system(f"python generate_dataset.py --n {i} --save_path ./datasets/{i}_cities.npy")
    # for i in range(150, 501, 50):
    #     os.system(f"python generate_dataset.py --n {i} --save_path ./datasets/{i}_cities.npy")
    for i in range(3, 16, 3):
        os.system(f"python generate_dataset.py --n {i} --ver 2 --save_path ./datasets2/{i}_cities.npy")
    for i in range(50, 101, 10):
        os.system(f"python generate_dataset.py --n {i} --ver 2 --save_path ./datasets2/{i}_cities.npy")
    for i in range(150, 501, 50):
        os.system(f"python generate_dataset.py --n {i} --ver 2 --save_path ./datasets2/{i}_cities.npy")