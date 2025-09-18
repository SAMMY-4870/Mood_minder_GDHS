import os

folder = "data/images/happy"
for i, filename in enumerate(os.listdir(folder)):
    ext = filename.split('.')[-1]
    new_name = f"happy_{i+1}.{ext}"
    old_path = os.path.join(folder, filename)
    new_path = os.path.join(folder, new_name)
    
    # Duplicate file exists तर skip करा
    if old_path != new_path and not os.path.exists(new_path):
        os.rename(old_path, new_path)

print("Renaming Done Safely!")
