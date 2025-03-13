import os
import shutil
import datetime

# Create backup directory if it doesn't exist
backup_dir = 'backup'
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# Get current timestamp for the backup filename
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# Main file to backup
main_file = 'multiplediseaseprediction.py'
if os.path.exists(main_file):
    backup_filename = f"{main_file}.{timestamp}.bak"
    backup_path = os.path.join(backup_dir, backup_filename)
    shutil.copy2(main_file, backup_path)
    print(f"Created backup: {backup_path}")

# Backup other Python files
for file in os.listdir('.'):
    if file.endswith('.py') and file != main_file and file != os.path.basename(__file__):
        backup_filename = f"{file}.{timestamp}.bak"
        backup_path = os.path.join(backup_dir, backup_filename)
        shutil.copy2(file, backup_path)
        print(f"Created backup: {backup_path}")

# Backup model files
for file in os.listdir('.'):
    if file.endswith('.pkl') or file.endswith('.h5') or file.endswith('.model'):
        backup_filename = f"{file}.{timestamp}.bak"
        backup_path = os.path.join(backup_dir, backup_filename)
        shutil.copy2(file, backup_path)
        print(f"Created backup: {backup_path}")

# Backup images directory if it exists
images_dir = 'images'
if os.path.exists(images_dir) and os.path.isdir(images_dir):
    images_backup_dir = os.path.join(backup_dir, 'images')
    if not os.path.exists(images_backup_dir):
        os.makedirs(images_backup_dir)
    
    for file in os.listdir(images_dir):
        file_path = os.path.join(images_dir, file)
        if os.path.isfile(file_path):
            backup_path = os.path.join(images_backup_dir, file)
            shutil.copy2(file_path, backup_path)
            print(f"Created backup: {backup_path}")

print("Backup completed successfully!") 