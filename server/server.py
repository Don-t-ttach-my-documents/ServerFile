from crypt import methods
import os

from flask import Flask, request, jsonify, make_response, send_file
import json
from werkzeug.utils import secure_filename
from databaseController import DBHandler


UPLOAD_FOLDER = 'doc'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

dbToken = DBHandler('db/tokenFile.db', "tokenTable")

PORT = 3200
HOST = '0.0.0.0'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1>Attachment document server</h1>", 200)

#Update
@app.route("/docs/<token_doc>", methods=['PUT'])
def updateDoc(token_doc):

	names = dbToken.getDataWithKey(token_doc)
	if (names is None): return make_response(jsonify({"error": "Link not found or deleted"}), 404)
	doc_name = names[0]

	# check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], doc_name)):
		return make_response(jsonify({"message" : "File not "+ doc_name +" found"}), 400)
	if file and allowed_file(file.filename):
		filename = secure_filename(doc_name)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		resp = jsonify({'message' : 'File successfully updated'})
		resp.status_code = 201
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
		resp.status_code = 400
		return resp

#Create
@app.route("/docs/upload", methods=['POST'])
def uploadDoc():
    # check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	filename = file.filename
	if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
		return make_response(jsonify({"error": "File already exist, please update it instead"}), 400)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		token = dbToken.addPath(filename)
		resp = jsonify({'token':token, 'url': "http://localhost:3200/docs/"+token, 'message' : 'File successfully uploaded'})
		resp.status_code = 201
		print(dbToken.getData())
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
		resp.status_code = 400
		return resp

#Delete
@app.route("/docs/<token_doc>", methods=['DELETE'])
def deleteDoc(token_doc):
	names = dbToken.getDataWithKey(token_doc)
	if (names is None): return make_response(jsonify({"error": "Link not found or deleted"}), 404)
	name_doc = names[0]
	try:
		os.remove(('{}/doc/'+str(name_doc)).format("."))
		return make_response(jsonify({"message '": "File"+name_doc+"' deleted!"}), 200)
	except FileNotFoundError as err:
		return make_response(jsonify({"error": str(err)}), 400)

#Read
@app.route("/docs/<token_doc>", methods=['GET'])
def getDoc(token_doc):
	names = dbToken.getDataWithKey(token_doc)
	print(names)
	print(dbToken.getData())
	if (names is None): return make_response(jsonify({"error": "Link not found or deleted"}), 404)
	name_doc = names[0]
	try:
		file = open(('{}/doc/'+str(name_doc)).format("."), "rb")
		return send_file(('{}/doc/'+str(name_doc)).format("."))
	except FileNotFoundError as err:
		return make_response(jsonify({"error": str(err)}), 400)
    
if __name__=="__main__":
	if not os.path.exists("doc"):
		os.mkdir("doc")
	print("Server running in port %s" % (PORT))
	app.run(host=HOST, port=PORT)


