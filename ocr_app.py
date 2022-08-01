# OCR App imports

# pip install pytesseract
import pytesseract
# pip install opencv-python
import cv2
import os

# Carga variables de entorno
from dotenv import load_dotenv
load_dotenv()

import numpy

# Google Lens
# pip install google-cloud-vision
import io
# import os
from google.cloud import vision
from google.cloud.vision_v1 import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gvision-358116-cdad80b21c64.json'


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

    
    



    results_list = []

    # Get txt files for each read image
    # text = pytesseract.image_to_string(img)
    # text_imout_grey = pytesseract.image_to_string(imout_grey)

    # Only for servers like PythonEverywhere
    # Fuente: https://stackoverflow.com/questions/48076964/path-error-with-tesseract
    # Fuente: https://stackoverflow.com/questions/63740198/how-to-use-tessdata-best-for-tesseract-pytesseract-what-are-the-arguments-and
    tessdata_dir_config = '--tessdata-dir "{}"'.format(os.getenv("TESSDATA_PREFIX"))
    print(tessdata_dir_config) # lang="spa"
    text_imout_grey = pytesseract.image_to_string(imout_grey, config=tessdata_dir_config)
    

    # print('text:', text)
    print()
    print('text_imout_grey:', text_imout_grey)

    if text_imout_grey != "" and text_imout_grey is not None:
        results_list.append(text_imout_grey)


    # region Test 2 - Threshold

    # Threshold to obtain binary image
    # Valores originales: imout_grey, 220, 255, cv2.THRESH_BINARY
    
    # Valores perfectos en local
    # 150, 235

    # Valores perfectos en server
    # 75, 222
    
    # Valores casi perfectos en local
    # imout_grey, 140, 235, cv2.THRESH_BINARY
    # imout_grey, 135, 222, cv2.THRESH_BINARY

    # Valores casi perfectos en SERVER
    # imout_grey, 115, 222, cv2.THRESH_BINARY


    # Resultados iguales
    # Valores casi perfectos en SERVER: imout_grey, 95, 222, cv2.THRESH_BINARY
    # Valores casi perfectos en SERVER: imout_grey, 95, 231, cv2.THRESH_BINARY
    # Valores casi perfectos en SERVER: imout_grey, 95, 240, cv2.THRESH_BINARY

    # 155, 240, lee mejor las comillas dobles, pero lee cosas innecesarias
    # 150, 235, lee mejor las comillas dobles, pero lee MÁS cosas innecesarias
    # 150, 247, lee mejor las comillas dobles, pero lee MÁS cosas innecesarias
    # 160, 248, solo lee bien Ender Lilies She whispers from the abyss,
    # todo lo demás lo lee mal y lee caracteres extra
    # 230, 248, solo lee el texto con una fuente con mayor grosor, las palabras
    # más finas desaparecen de la imagen
    # 150, 247, lee mejor las comillas dobles, pero lee mal la letra B en Bound
    # 170, 248, lee MAL las comillas dobles, y lee mal la letra B en Bound, la lee como S
    # 210, 248, solo lee mal la letra B en Bound, ni la lee
    # 190, 240, la B de Bound la lee como un espacio y una letra s
    # 190, 235, exactamente mismo resultado que el anterior
    thresh = cv2.threshold(imout_grey, 150, 235, cv2.THRESH_BINARY)[1] # 75, 222

    # Create custom kernel, funciona también con (1,1)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    # Perform closing (dilation followed by erosion)
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Invert image to use for Tesseract
    result = 255 - close

    # Get txt files for each read image
    text_result = pytesseract.image_to_string(result, config=tessdata_dir_config)

    print('GaussianBlur result:', text_result)
    print()

    if len(text_result) != 0:
        results_list.append(text_result)

    # endregion


    # region Test 3 - New Preprocessing

    # Fuente: https://stackoverflow.com/questions/62953886/reading-numbers-using-pytesseract
    # Page segmentation mode, PSM was changed to 6 since each page is a single uniform text block.
    # custom_config = r'--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'

    # # load the image as grayscale
    # # img = cv2.imread("5.png",cv2.IMREAD_GRAYSCALE)
    # img = imout_grey

    # # Change all pixels to black, if they aren't white already (since all characters were white)
    # img[img != 255] = 0

    # # Scale it 10x
    # scaled = cv2.resize(img, (0,0), fx=10, fy=10, interpolation = cv2.INTER_CUBIC)

    # # Retained your bilateral filter
    # filtered = cv2.bilateralFilter(scaled, 11, 17, 17)

    # # Thresholded OTSU method
    # thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # # Erode the image to bulk it up for tesseract
    # kernel = numpy.ones((4,4),numpy.uint8)
    # eroded = cv2.erode(thresh, kernel, iterations = 2)

    # pre_processed = eroded

    # # Feed the pre-processed image to tesseract and print the output.
    # ocr_text = pytesseract.image_to_string(pre_processed, config=custom_config)
    # if len(ocr_text) != 0:
    #     print("Test 3 ocr_text:",ocr_text)
    #     results_list.append(ocr_text)
    # else: print("No string detected in test 3")

    

    custom_config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'
    
    thresh = cv2.threshold(imout_grey, 75, 222, cv2.THRESH_BINARY)[1] # 150, 235

    # Create custom kernel, funciona también con (1,1)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    # Perform closing (dilation followed by erosion)
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Invert image to use for Tesseract
    result = 255 - close

    # Get txt files for each read image
    ocr_text = pytesseract.image_to_string(result, config=custom_config)

    print('GaussianBlur result:', ocr_text)
    print()

    # if len(text_result) != 0:
    #     results_list.append(text_result)
    if len(ocr_text) != 0:
        print("Test 3 ocr_text:",ocr_text)
        results_list.append(ocr_text)
    else: print("No string detected in test 3")


    # endregion

    # region Test 4 

    # Fuente: https://stackoverflow.com/questions/23260345/opencv-binary-adaptive-threshold-ocr/23260699#23260699
    image = cv2.imread(IMAGE_PATH, cv2.IMREAD_GRAYSCALE) # reading image
    tessdata_dir_config = '--tessdata-dir "{}"'.format(os.getenv("TESSDATA_PREFIX"))
    if image is None:
        print('Can not find the image!')
        exit(-1)

    # Thresholding image using ostu method
    # Original
    # ret, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    ret, thresh = cv2.threshold(image, 150, 235, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    # Applying closing operation using ellipse kernel
    # N = 3 # Valor Original
    # N = 7 # Con 7 lee mejor el medidor de agua de Joshua, con 9 también funciona decente
    N = 3 # 13 y 17 más o menos: 1 596\n
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (N, N))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    ocr_text = pytesseract.image_to_string(thresh, config=tessdata_dir_config)
    if len(ocr_text) != 0:
        print("Test 4 ocr_text:",ocr_text)
        results_list.append(ocr_text)
    else: print("No string detected in test 4")

    # endregion


    #region Show imgs (disable later)

    # Shows images in screen to user
    cv2.imshow('img', img)
    cv2.imshow('imout', imout)
    # cv2.imshow('imout_grey', imout_grey)
    cv2.imshow('result', result)
    cv2.imshow('thresh', thresh)

    cv2.waitKey(0)

    # close all open windows
    cv2.destroyAllWindows()

    #endregion


    remove_picture(IMAGE_PATH)
    
    if os.path.exists(IMAGE_PATH):
        print("File still exists.")


    # print(results_list)
    return results_list

    return text_imout_grey, text_result

# endregion


# region OCR Google Lens API

"""
    img_path: Ruta donde se encuentra la imagen que se quiere leer.
"""
def ocr_gLens_api(img_path):

    results_list = []

    IMAGE_PATH = img_path

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    #set this thumbnail as the url
    image = types.Image()

    # IMAGE_PATH = 'number3.jpg'

    with io.open(IMAGE_PATH, 'rb') as image_file:        
            content = image_file.read()  

    image = vision.Image(content=content)


    # Se crea una celda en VsCode -> # %%
    #### TEXT DETECTION ######

    response_text = client.text_detection(image=image) # image

    # for r in response_text.text_annotations:
    #     d = {
    #         'text': r.description
    #     }
    #     print(d)
        # Resultados:
        #{'text': '38762'}
        #{'text': '38762'}

    glens_results = response_text.text_annotations
    print("glens_results:", glens_results)
    
    text_result = ""

    # Lista vacía = []
    if not glens_results:
        print("List is empty")
        text_result = "Error en la obtención de resultados."
    
    # Lista NO está vacía
    if glens_results:
        text_result = response_text.text_annotations[0].description
        print("text_result:", text_result)
        # Resultado:
        # 38762


    results_list.append(text_result)
    results_list.append("")
    results_list.append("")
    results_list.append("")


    remove_picture(IMAGE_PATH)
    
    if os.path.exists(IMAGE_PATH):
        print("File still exists.")


    # print(results_list)
    return results_list

# endregion


# Fuente: https://appdividend.com/2021/08/13/how-to-delete-file-if-exists-in-python/#:~:text=To%20delete%20a%20file%20if,remove()%20method.
def remove_picture(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print("The file has been deleted successfully")
    else:
        print("The file does not exist!")


