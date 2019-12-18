# Tutorial:
# https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
# https://www.geeksforgeeks.org/flask-creating-first-simple-application/

from flask import Flask, jsonify, abort, make_response, request, url_for, \
                    render_template, redirect
import base64 # to decode MIME base64 encoded by canvas.toDataURI() in JavaScript
import mimetypes

from textdetect import textdetect as td
from database import search_items

app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route('/canvas', methods = ['POST'])
def save_image():
    
    image_data = request.form['image']
    image_data_str = image_data.split(',')[1]    
    image_data_decode = base64.b64decode(image_data_str)

    text_list = td.text_detect(image_data_decode)
    print(" === Finish text_detect ===")
    print(text_list)

    result = search_items(text_list)
    print("\n === Matched item ===")
    print(result)

    return jsonify(result)



if __name__ == '__main__':
    app.run(debug=True)
