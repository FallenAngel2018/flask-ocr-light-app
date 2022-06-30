# OCR App imports

# pip install pytesseract
import pytesseract
# pip install opencv-python
import cv2
import os

# Carga variables de entorno
from dotenv import load_dotenv
load_dotenv()

# region OCR App method

"""
    img_path: Ruta donde se encuentra la imagen que se quiere leer.
"""
def ocr_app_get_text(img_path):
    
    # FOR WINDOWS (uncomment if executed in local Windows pc)
    # If you don't have tesseract executable in your PATH, include the following:
    # pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract'
    # pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files (x86)/Tesseract-OCR/tesseract'


    IMAGE_PATH = img_path

    img = cv2.imread(IMAGE_PATH)

    # More quality image
    imout = cv2.detailEnhance(img)

    # More quality in binarized image 
    imout_grey = cv2.cvtColor(imout, cv2.COLOR_BGR2GRAY)

    print('IMAGE_PATH:', IMAGE_PATH)


    # Get txt files for each read image
    # text = pytesseract.image_to_string(img)
    # text_imout_grey = pytesseract.image_to_string(imout_grey)

    # Only for servers like PythonEverywhere
    # Fuente: https://stackoverflow.com/questions/48076964/path-error-with-tesseract
    # Fuente: https://stackoverflow.com/questions/63740198/how-to-use-tessdata-best-for-tesseract-pytesseract-what-are-the-arguments-and
    tessdata_dir_config = '--tessdata-dir "{}"'.format(os.getenv("TESSDATA_PREFIX"))
    print(tessdata_dir_config)
    # text_imout_grey = pytesseract.image_to_string(imout_grey, config=tessdata_dir_config)
    

    # print('text:', text)
    print()
    # print('text_imout_grey:', text_imout_grey)


    remove_picture(IMAGE_PATH)
    
    if os.path.exists(IMAGE_PATH):
        print("File still exists.")


    # Threshold to obtain binary image
    # Valores originales: imout_grey, 220, 255, cv2.THRESH_BINARY
    # Valores perfectos en local: imout_grey, 150, 235, cv2.THRESH_BINARY
    # Valores casi perfectos en local: imout_grey, 135, 222, cv2.THRESH_BINARY
    thresh = cv2.threshold(imout_grey, 115, 222, cv2.THRESH_BINARY)[1] # 125, 225

    # Create custom kernel, funciona también con (1,1)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    # Perform closing (dilation followed by erosion)
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Invert image to use for Tesseract
    result = 255 - close

    # Get txt files for each read image
    text_result = pytesseract.image_to_string(result, config=tessdata_dir_config)

    print('GaussianBlur result:', text_result)

    # return text_imout_grey 
    return text_result

# endregion


# Fuente: https://appdividend.com/2021/08/13/how-to-delete-file-if-exists-in-python/#:~:text=To%20delete%20a%20file%20if,remove()%20method.
def remove_picture(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print("The file has been deleted successfully")
    else:
        print("The file does not exist!")


