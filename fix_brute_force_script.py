import os

def fix(base_dir):
    for f in os.listdir(base_dir):
        new = f.replace("brute_force", "bruteForce")
        os.system(f"mv {base_dir}/{f} {base_dir}/{new}")
