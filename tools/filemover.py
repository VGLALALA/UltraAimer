import os
import shutil

# Paths
root_folder = '/home/vglalala/UltraAimer/100kCS/images'
train_images_folder = '/home/vglalala/UltraAimer/100kCS/train/images'
train_labels_folder = '/home/vglalala/UltraAimer/100kCS/train/labels'
val_images_folder = '/home/vglalala/UltraAimer/100kCS/val/images'
val_labels_folder = '/home/vglalala/UltraAimer/100kCS/val/labels'
test_images_folder = '/home/vglalala/UltraAimer/100kCS/test/images'
test_labels_folder = '/home/vglalala/UltraAimer/100kCS/test/labels'

# Create necessary directories
os.makedirs(train_images_folder, exist_ok=True)
os.makedirs(train_labels_folder, exist_ok=True)
os.makedirs(val_images_folder, exist_ok=True)
os.makedirs(val_labels_folder, exist_ok=True)
os.makedirs(test_images_folder, exist_ok=True)
os.makedirs(test_labels_folder, exist_ok=True)

# Get list of all images and shuffle them
all_images = [f for f in os.listdir(root_folder) if f.endswith('.jpg')]
all_images.sort()  # Ensure a consistent order for reproducibility

# Split the dataset
train_split = all_images[:70000]
val_split = all_images[70000:90000]
test_split = all_images[90000:]


# Function to copy images and labels
def copy_files(file_list, dest_images_folder, dest_labels_folder):
    for filename in file_list:
        # Copy image file
        src_image = os.path.join(root_folder, filename)
        dest_image = os.path.join(dest_images_folder, filename)
        shutil.copyfile(src_image, dest_image)

        # Copy label file
        label_filename = filename.replace('.jpg', '.txt')
        src_label = os.path.join(root_folder, label_filename)
        dest_label = os.path.join(dest_labels_folder, label_filename)

        if os.path.exists(src_label):
            shutil.copyfile(src_label, dest_label)


# Copy the files
copy_files(train_split, train_images_folder, train_labels_folder)
copy_files(val_split, val_images_folder, val_labels_folder)
copy_files(test_split, test_images_folder, test_labels_folder)

print("Files have been copied successfully.")
