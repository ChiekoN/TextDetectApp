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

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Veges, Apples, Egg, Tomato sauce',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Master Flask and REST API',
        'done': False       
    }
]

comment = ""

# Convert task id to task's url
def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['url'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        comment = request.form['cmt']
        print("comment = {}".format(comment))
        return jsonify({'comment' : comment})
    else : # GET
        return render_template("index.html")


@app.route('/canvas', methods = ['POST'])
def save_image():
    print("\n ------ In save_image()")

    print("request.accept_mimetypes={}".format(request.accept_mimetypes))
    print("request.content_encoding={}".format(request.content_encoding))
    print("request.content_type={}".format(request.content_type))
    print("request.data={}".format(request.data))
    print("request.mimetype_params={}".format(request.mimetype_params))
    print("request.args={}".format(request.args))
    #print("request.form={}".format(request.form))
    print("request.form['check']={}".format(request.form['check']))
    print(" ----- ")
    
    image_data = request.form['image']
    #print("--- image_data = {}".format(image_data))
    image_data_str = image_data.split(',')[1]
    
    image_data_decode = base64.b64decode(image_data_str)
    #with open("canvas.png", "bw") as f:
    #    f.write(image_data_decode)

    text_list = td.text_detect(image_data_decode)
    print(" === Finish text_detect ===")
    print(text_list)

    result = search_items(text_list)

    print("\n === Matched item ===")
    print(result)

    #return redirect(url_for('index'))
    return jsonify(result)
    


# Show the task list
@app.route('/todo', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': [make_public_task(task) for task in tasks]})


# Flask's default `abort(404)` outputs HTML syntax, 
# but we need to make it in JSON
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# Show a certain task by specifying task id
@app.route('/todo/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


# Add tasks
@app.route('/todo', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'], # Return 'title' contents
        'description': request.json.get('description', ""), # Return description if it exists,
                                                            # otherwise return ""
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201  #201:Created

# Modify/update tasks
@app.route('/todo/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json: # Signal sent was not JSON format
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)

    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})


# Delete task
@app.route('/todo/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})




if __name__ == '__main__':
    app.run(debug=True)
