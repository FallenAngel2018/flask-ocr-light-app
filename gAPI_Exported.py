# %%
import io
import os

# %%
#pip install google-cloud-vision

# %%

from google.cloud import vision
from google.cloud.vision_v1 import types

# %%
#the JSON file you downloaded in step 5 above
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gvision-358116-cdad80b21c64.json'

# %%
# Instantiates a client
client = vision.ImageAnnotatorClient()

# %%
#set this thumbnail as the url
image = types.Image()

path = 'number3.jpg'

with io.open(path, 'rb') as image_file:        
    	content = image_file.read()  

image = vision.Image(content=content)


# %%
#### TEXT DETECTION ######

response_text = client.text_detection(image=image) # image

for r in response_text.text_annotations:
    d = {
        'text': r.description
    }
    print(d)

# %%
texto = response_text.text_annotations[0].description
print(texto)


