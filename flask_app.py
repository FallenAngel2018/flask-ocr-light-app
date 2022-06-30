
# pip install flask
from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename

from datetime import datetime

from pprint import pprint
import os

# from dotenv import load_dotenv
# load_dotenv()

from ocr_app import ocr_app_get_text
# To copy files
import shutil

app = Flask(__name__,
            template_folder='./templates',)


UPLOAD_FOLDER = r'static/uploads/' # Original, funciona en Windows
TRAINED_FONTS_SOURCE = r"./static/trained_fonts/"
OCR_RESULTS_UPLOAD = r'./static/ocr_results/' # Funciona en Windows

TRAINED_FONTS_DESTINATION_1 = r"../../../usr/share/tesseract-ocr/4.00/tessdata/"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TRAINED_FONTS_SOURCE'] = TRAINED_FONTS_SOURCE
app.config['OCR_RESULTS_UPLOAD'] = OCR_RESULTS_UPLOAD

app.config['TRAINED_FONTS_DESTINATION_1'] = TRAINED_FONTS_DESTINATION_1

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# region Before First Request Methods (Only use True to log on Heroku server)

source_folder = app.config['TRAINED_FONTS_SOURCE']
destination_folder = app.config['TRAINED_FONTS_DESTINATION_1']

def check_some_folders_existance(show):
    if show:
        source_folder_exists = os.path.isdir(source_folder)
        exists = os.path.isdir(destination_folder)
        
        print('source_folder_exists:', source_folder_exists)
        print('destination exists:', exists)

        if exists != False and (exists != None or exists != ''):
            print('Dir. exists!')
        else:
            print('Dir. not exists')

        print("before_first_request")


        # Fetch all files
        for file_name in os.listdir(source_folder):
            # construct full file path
            source = source_folder + file_name
            destination = destination_folder + file_name

            # copy only files
            # El propósito de esta sección, es agregar en el servidor de Heroku
            # los .traineddata para que el server lea mejor las imágenes.
            # Esto se debe lograr como sea, ya sea por copia y pega de archivos,
            # o por la descarga de esos archivos desde una nube externa y agregadas
            # a las carpetas de destination 1 y 2.
            if os.path.isfile(source):
                # print('destination:', destination)
                # print('source:', source)

                # Descomentar cuando se suba a Heroku, esto copia los archivos
                # No se copiaron, habrá que hacer más pruebas
                shutil.copy(source, destination)
                print(file_name,'copied!')


                # Aquí falta código de descarga de .traineddata de nube en Mega

                # Y una vez obtenidos y listados los archivos
                # en un arreglo llamado files...
                # for f in files:
                #     shutil.move(f, 'destination')
                #     shutil.move(f, 'destination2')

# endregion

check_some_folders_existance(False)



# region Html pages

@app.route('/')
# @app.route('/', methods=['GET'])
def index():
    return render_template("index.html", title="Index")

@app.route('/index3')
def index_3():
    return render_template("index3.html", title="Index 3")

@app.route('/base_html')
def base_html(title=None):
    return render_template("base.html", title = title)

@app.route('/result')
def html_result(result=None):
    return render_template("result.html", result = result)

@app.route('/result2')
def html_result2(result=None):
    return render_template("result2.html", result = result)

# endregion


# En Index, url_for('upload_file_test') apunta a este método
# sin importar la ruta que tenga definida
@app.route('/upload_test', methods=['POST'])
def upload_file_test():
    # Getting files uploaded in form enctype="multipart/form-data"
    files = request.files['files[]']
    
    message, result, status_code = upload_file(files)

    # pprint(vars(result))
    # print('result.response["ocr_extracted_text"]:', result.response["ocr_extracted_text"])
    # print('result.response[0]:', result.response[0])

    if status_code == 200 or status_code == 201:  
        return render_template("result2.html", result = result)
    else: # Para probar esteescenario, en el if dejar solo el status_code == 200
        return render_template("result.html", result = message)


@app.route('/upload', methods=['POST'])
def upload_file():

    # Obtiene del campo 'files[]' en el request hecho por el usuario los archivos que contenga
    files = request.files.getlist('files[]')
    message, result, status_code = upload_file(files)

    print('result:', result)

    if status_code == 200 or status_code == 201:  
        return render_template("result2.html", result = result)
    else: # Para probar este escenario, en el if dejar solo el status_code == 200
        return render_template("result.html", result = message)



def upload_file(files):
    # Check if the post request has the file part
    if 'files[]' not in request.files and 'photo' not in request.files:
        # resp = jsonify({'message' : 'No file part in the request'})
        # resp = jsonify({'message' : 'No file uploaded in the request :/, go back and upload some.'})
        errors['message'] = 'No file uploaded in the request :/, go back and upload some.'
        resp = jsonify(errors)
        resp.status_code = 400
        resp.content_type = "application/json"
        # return resp
        return errors, "No file uploaded", 400

    # Obtiene del campo 'files[]' en el request hecho por el usuario los archivos que contenga
    files = request.files.getlist('files[]')
     
    errors = {}
    success = False

    for file in files:      
        if file and allowed_file(file.filename):
            print(file)
            # pprint(vars(file))

            filename = file.filename

            # Get file extension
            ext = '.' in filename and filename.rsplit('.', 1)[1].lower()

            filename = secure_filename(file.filename)

            # datetime object containing current date and time
            now = datetime.now()

            # date and time: dd/mm/YY H:M:S
            dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

            # Para que sea un nombre único, se agrega
            # la fecha y hora en la que se hizo la consulta
            filename = filename + "_" + dt_string + "." + ext

            dir = app.config['UPLOAD_FOLDER']
            print("exists upload:", os.path.exists(dir))
            cwd = os.getcwd()
            print("Current folder:", cwd)

            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(photo_path)
            # file.save(r"" + photo_path)

            size = os.path.getsize(photo_path)
            print("size:", size, "bytes")

            success = True
        else:
            errors[file.filename] = 'File type is not allowed'
 
    if success and errors:
        """ Así mostraría el mensaje
            {
                "message": "Files successfully uploaded, but some errors occurred."
            }
        """
        errors['message'] = 'File(s) successfully uploaded, but some errors occurred.'
        resp = jsonify(errors)
        resp.status_code = 500
        resp.content_type = "application/json"
        # return resp
        return errors, errors['message'], 500


    if success:
        # Type (print(type(resp))): flask.wrappers.Response
        resp = jsonify({'message' : 'Files successfully uploaded'})
        # resp.status_code = 201
        # resp.content_type = "application/json"

        ocr_text_result = ocr_app_get_text(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        # Si el texto extraído no está vacío...
        if ocr_text_result != '':

            message = 'Files successfully uploaded'
            ocr_text_result = ocr_text_result.replace("\n\n", " ").replace("\u201c", '\"').replace("\u201d", '"').replace("\\", "")

            # if upload_success:
            # replace is only for making json esthetic, when returned, left the \n\n and else
            resp = jsonify({
                'message' : message,
                'ocr_extracted_text': ocr_text_result
            })

        return message, ocr_text_result, 201
    else:
        resp = jsonify(errors) 
        resp.status_code = 500
        resp.content_type = "application/json"
        # return resp
        return errors, errors['message'], 500




if __name__ == '__main__':
    # app.config['SESSION_TYPE'] = 'filesystem'

    app.run() # ,debug = True
    # # Only use in localhost
    # app.run(port = 7000) # ,debug = True

