# OCR App imports

# pip install pytesseract
import pytesseract
# pip install opencv-python
import cv2
import os


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
    text = pytesseract.image_to_string(img)
    text_imout_grey = pytesseract.image_to_string(imout_grey)

    print('text:', text)
    print()
    print('text_imout_grey:', text_imout_grey)


    remove_picture(IMAGE_PATH)
    
    if os.path.exists(IMAGE_PATH):
        print("File still exists.")

    return text_imout_grey

# endregion


# Fuente: https://appdividend.com/2021/08/13/how-to-delete-file-if-exists-in-python/#:~:text=To%20delete%20a%20file%20if,remove()%20method.
def remove_picture(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print("The file has been deleted successfully")
    else:
        print("The file does not exist!")


