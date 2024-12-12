import os,os.path,shutil
import subprocess

top = "samples"
target = "DQ"

# copy
if os.path.exists(target):
    shutil.rmtree(target)
shutil.copytree(os.path.join("..", top, target), target)
shutil.copytree(os.path.join("..", "xmlui"), os.path.join(target, "xmlui"))

# clear cache
for root, dirs, files in os.walk(target):
    for dir in dirs:
        if dir == "__pycache__":
            shutil.rmtree(os.path.join(root, dir))

# create package
subprocess.run(["pyxel", "package", target, os.path.join(target, "main.py")])


# remove
shutil.rmtree(target)
