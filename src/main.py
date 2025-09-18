import os
import random
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import image_dataset_from_directory

# ------------------- Preprocess (Safe Rename) -------------------
def safe_rename_images():
    folder = "data/images/happy"
    if not os.path.exists(folder):
        print(f"Folder {folder} does not exist!")
        return
    for i, filename in enumerate(os.listdir(folder)):
        ext = filename.split('.')[-1]
        new_name = f"happy_{i+1}.{ext}"
        old_path = os.path.join(folder, filename)
        new_path = os.path.join(folder, new_name)
        if old_path != new_path and not os.path.exists(new_path):
            os.rename(old_path, new_path)
    print("Renaming Done Safely!")

# ------------------- Display Random Quote -------------------
def display_random_quote():
    quotes_file = 'data/quotes/quotes.csv'
    images_folder = 'data/images/happy'
    
    if not os.path.exists(quotes_file):
        print(f"Quotes file {quotes_file} not found!")
        return
    if not os.path.exists(images_folder):
        print(f"Images folder {images_folder} not found!")
        return
    
    quotes = pd.read_csv(quotes_file)
    if quotes.empty:
        print("Quotes file is empty!")
        return

    image_files = os.listdir(images_folder)
    if not image_files:
        print("No images found!")
        return
    
    # random image + quote
    img_file = random.choice(image_files)
    quote_row = quotes.sample().iloc[0]

    img_path = os.path.join(images_folder, img_file)
    img = load_img(img_path, target_size=(200, 200))
    img_array = img_to_array(img) / 255.0
    
    plt.imshow(img_array)
    plt.axis('off')
    plt.title(f"{quote_row['quote']} \n— {quote_row['author']}", fontsize=12)
    plt.show()

# ------------------- Train Model -------------------
def train_model():
    train_dir = 'data/images/happy'
    if not os.path.exists(train_dir):
        print(f"Training folder {train_dir} not found!")
        return
    
    print("Starting Model Training...")
    dataset = image_dataset_from_directory(train_dir, batch_size=32, image_size=(200, 200), label_mode='categorical')
    class_names = dataset.class_names
    print(f"Classes found: {class_names}")
    
    model = Sequential([
        Conv2D(32, (3,3), activation='relu', input_shape=(200, 200, 3)),
        MaxPooling2D(2,2),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(len(class_names), activation='softmax')
    ])
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(dataset, epochs=5)
    model.save('happy_model.h5')
    print("Model Trained and Saved as happy_model.h5")

# ------------------- Main -------------------
if __name__ == "__main__":
    safe_rename_images()
    display_random_quote()
    train_model()
