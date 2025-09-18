import pandas as pd
import random
import os
from PIL import Image
import matplotlib.pyplot as plt

# Load quotes
quotes = pd.read_csv('data/quotes/quotes.csv')

# Select random quote
quote = random.choice(quotes['quote'])

# Select random image
image_files = os.listdir('data/images/happy')
image_path = os.path.join('data/images/happy', random.choice(image_files))
img = Image.open(image_path)

# Show image with quote
plt.imshow(img)
plt.axis('off')
plt.title(quote)
plt.show()
