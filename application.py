# Importing modules
from flask import Flask, render_template, request, jsonify, redirect, session
from flask import abort
from flask_cors import CORS, cross_origin
from flask import make_response, url_for
import json
import random
from pymongo import MongoClient
from time import gmtime, strftime
import sqlite3


# connection to MongoDB Database
connection = MongoClient("mongodb://Admin:Admin123@cluster0-shard-00-00-cj2z4.azure.mongodb.net:27017,cluster0-shard-00-01-cj2z4.azure.mongodb.net:27017,cluster0-shard-00-02-cj2z4.azure.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")

# Object creation
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = '<some secret key>'
CORS(app)

# Initialize Database
def create_mongodatabase():
    try:
        dbnames = connection.database_names()
        if 'cloud_native' not in dbnames:
            db = connection.cloud_native.users
            db_reviews = connection.cloud_native.reviews
            db_api = connection.cloud_native.apirelease

            db.insert({
            "email": "eric.strom@google.com",
            "id": 33,
            "name": "Eric stromberg",
            "password": "eric@123",
            "username": "eric.strom"
            })

            db_reviews.insert({
            "body": "New blog post,Launch your app with the AWS Startup Kit! #AWS",
            "id": 18,
            "timestamp": "2017-03-11T06:39:40Z",
            "reviewedby": "eric.strom"
            })

            db_api.insert( {
              "buildtime": "2017-01-01 10:00:00",
              "links": "/api/v1/users",
              "methods": "get, post, put, delete",
              "version": "v1"
            })
            db_api.insert( {
              "buildtime": "2017-02-11 10:00:00",
              "links": "api/v2/reviews",
              "methods": "get, post",
              "version": "2017-01-10 10:00:00"
            })
            print ("Database Initialize completed!")
        else:
            print ("Database already Initialized!")
    except:
        print ("Database creation failed!!")

# List users
def list_users():
    api_list=[]
    db = connection.cloud_native.users
    for row in db.find({}, {'_id':0}):
        api_list.append(row)
    # print (api_list)
    return jsonify({'user_list': api_list})

# List specific users
def list_user(user_id):
    print (user_id)
    api_list=[]
    db = connection.cloud_native.users
    for i in db.find({'id':user_id}):
        api_list.append(str(i))

    if api_list == []:
        abort(404)
    return jsonify({'user_details':api_list})

# List specific review
def list_review(user_id):
    print (user_id)
    db = connection.cloud_native.reviews
    api_list=[]
    review = db.find({'id':user_id})
    for i in review:
        api_list.append(str(i))
    if api_list == []:
        abort(404)
    return jsonify({'review': api_list})

# Adding user
def add_user(new_user):
    api_list=[]
    print (new_user)
    db = connection.cloud_native.users
    user = db.find({'$or':[{"username":new_user['username']} ,{"email":new_user['email']}]})
    for i in user:
        print (str(i))
        api_list.append(str(i))

    # print (api_list)
    if api_list == []:
    #    print(new_user)
       db.insert(new_user)
       return "Success"
    else :
       abort(409)

# Deleting User
def del_user(del_user):
    db = connection.cloud_native.users
    api_list=[]
    for i in db.find({'username':del_user}):
        api_list.append(str(i))

    if api_list == []:
        abort(404)
    else:
       db.remove({"username":del_user})
       return "Success"

# List reviews
def list_reviews():
    api_list=[]
    db = connection.cloud_native
    for row in db.reviews.find({}, {'_id':0}):
        api_list.append(row)
    # print (api_list)
    return jsonify({'reviews_list': api_list})

# Adding reviews
def add_review(new_review):
    api_list=[]
    print (new_review)
    db_user = connection.cloud_native.users
    db_review = connection.cloud_native.reviews

    user = db_user.find({"username":new_review['username']})
    for i in user:
        api_list.append(str(i))
    if api_list == []:
       abort(404)
    else:
        db_review.insert(new_review)
        return "Success"

def upd_user(user):
    api_list=[]
    print (user)
    db_user = connection.cloud_native.users
    users = db_user.find_one({"id":user['id']})
    for i in users:
        api_list.append(str(i))
    if api_list == []:
       abort(409)
    else:
        db_user.update({'id':user['id']},{'$set': user}, upsert=False )
        return "Success"

# API Routes
@app.route('/')
def main():
    return render_template('main.html')


@app.route('/addname')
def addname():
  if request.args.get('yourname'):
    session['name'] = request.args.get('yourname')
    # Redirect to main
    return redirect(url_for('main'))
  else:
    # getting addname
    return render_template('addname.html', session=session)

@app.route('/clear')
def clearsession():
    # Clear the session
    session.clear()
    # Redirect the user to the main page
    return redirect(url_for('main'))

@app.route('/adduser')
def adduser():
    return render_template('adduser.html')

@app.route('/addreviews')
def addreviewjs():
    return render_template('addreviews.html')

@app.route("/api/v1/info")
def home_index():
    api_list=[]
    db = connection.cloud_native.apirelease
    for row in db.find():
        api_list.append(str(row))
    return jsonify({'api_version': api_list}), 200



@app.route('/api/v1/users', methods=['GET'])
def get_users():
    return list_users()

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return list_user(user_id)


@app.route('/api/v1/users', methods=['POST'])
def create_user():
    if not request.json or not 'username' in request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400)
    user = {
        'username': request.json['username'],
        'email': request.json['email'],
        'name': request.json.get('name',""),
        'password': request.json['password'],
        'id': random.randint(1,1000)
    }
    return jsonify({'status': add_user(user)}), 201

@app.route('/api/v1/users', methods=['DELETE'])
def delete_user():
    if not request.json or not 'username' in request.json:
        abort(400)
    user=request.json['username']
    return jsonify({'status': del_user(user)}), 200


@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = {}
    user['id']=user_id
    key_list = request.json.keys()
    for i in key_list:
        user[i] = request.json[i]
    return jsonify({'status': upd_user(user)}), 200

@app.route('/api/v2/reviews', methods=['GET'])
def get_reviews():
    return list_reviews()

@app.route('/api/v2/reviews', methods=['POST'])
def add_reviews():

    user_review = {}
    if not request.json or not 'username' in request.json or not 'body' in request.json:
        abort(400)
    user_review['username'] = request.json['username']
    user_review['body'] = request.json['body']
    user_review['timestamp']=strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
    user_review['id'] = random.randint(1,1000)

    return  jsonify({'status': add_review(user_review)}), 201

@app.route('/api/v2/reviews/<int:id>', methods=['GET'])
def get_review(id):
    return list_review(id)

# Error handling
@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify({'error': 'Resource not found!'}), 404)

@app.errorhandler(409)
def user_found(error):
    return make_response(jsonify({'error': 'Conflict! Record exist'}), 409)

@app.errorhandler(400)
def invalid_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

# Main Function
if __name__ == '__main__':
    create_mongodatabase()
    app.run(host='0.0.0.0', port=5000, debug=True)
