import os

def fix(base_dir):
    for f in os.listdir(base_dir):
        new = f.replace("brute_force", "bruteForce")
        os.system(f"mv {base_dir}/{f} {base_dir}/{new}")

if __name__ == '__main__':
    fix("noa_kirel/results/small")