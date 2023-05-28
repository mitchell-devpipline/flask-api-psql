import psycopg2
from flask import Flask, jsonify, request

conn = psycopg2.connect('dbname=usermgt host=localhost')
cursor = conn.cursor()
app = Flask(__name__)

# Create the Database


def create_all():
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS Users (
         user_id SERIAL PRIMARY KEY,
         first_name VARCHAR NOT NULL,
         last_name VARCHAR,
         email VARCHAR NOT NULL UNIQUE,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         org_id int,
         active smallint
      );
   """)
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS Organizations (
         org_id SERIAL PRIMARY KEY,
         name VARCHAR NOT NULL,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         active smallint
      );
   """)
    print("Creating tables...")
    conn.commit()

# Route to Add User to Database


@app.route('/user/add', methods=['POST'])
def user_add():
    post_data = request.form if request.form else request.json
    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    email = post_data.get('email')
    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    org_id = post_data.get('org_id')
    active = post_data.get('active')

    cursor.execute(
        "INSERT INTO USERS (first_name, last_name, email, phone, city, state, org_id, active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        [first_name, last_name, email, phone, city, state, org_id, active])
    conn.commit()
    # add_user(first_name, last_name, email, phone, city, state, org_id, active)

    return jsonify("User created"), 201


@app.route('/users', methods=["GET"])
def get_all_active_users():
    cursor.execute(
        "SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM Users WHERE active = 1;")
    results = cursor.fetchall()
    if not results:
        return jsonify('No Users in Table'), 404
    else:
        results_list = []
        for result in results:
            result_dict = {
                "user_id": result[0],
                "first_name": result[1],
                "last_name": result[2],
                "email": result[3],
                "phone": result[4],
                "city": result[5],
                "state": result[6],
                "org_id": result[7],
                "active": result[8]
            }
            results_list.append(result_dict)
        return jsonify(results_list), 200


@app.route('/user/<id>', methods=["GET"])
def get_user_by_id(id):
    cursor.execute(
        "SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM Users WHERE user_id = %s;",
        [id])
    result = cursor.fetchone()

    if not result:
        return jsonify('That user does not exist'), 404
    else:

        result_dict = {
            "user_id": result[0],
            "first_name": result[1],
            "last_name": result[2],
            "email": result[3],
            "phone": result[4],
            "city": result[5],
            "state": result[6],
            "org_id": result[7],
            "active": result[8]
        }

        return jsonify(result_dict), 200


@app.route('/user/activate/<id>', methods=["PATCH"])
def activate_user(id):
    cursor.execute("UPDATE Users SET active = 1 WHERE user_id = %s", [id])
    conn.commit()
    return jsonify("User Activated"), 200


@app.route('/user/deactivate/<id>', methods=["PATCH"])
def deactivate_user(id):
    cursor.execute("UPDATE Users SET active = 0 WHERE user_id = %s", [id])
    conn.commit()
    return jsonify("User Deactivated"), 200


@app.route('/user/update/<id>', methods=["PUT"])
def update_user_by_id(id):
    cursor.execute(
        "SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM Users WHERE user_id =%s;",
        [id])
    result = cursor.fetchone()

    if not result:
        return jsonify('That user does not exist'), 404
    else:

        result_dict = {
            "user_id": result[0],
            "first_name": result[1],
            "last_name": result[2],
            "email": result[3],
            "phone": result[4],
            "city": result[5],
            "state": result[6],
            "org_id": result[7],
            "active": result[8]
        }

    post_data = request.form if request.form else request.json

    for key, val in post_data.copy().items():
        if not val:
            post_data.pop(key)

    result_dict.update(post_data)

    cursor.execute(
        '''UPDATE Users SET 
        first_name = %s, 
        last_name= %s, 
        email= %s, 
        phone= %s, 
        city= %s, 
        state= %s, 
        org_id= %s, 
        active= %s 
        
        WHERE user_id = %s
    ;''',
        [result_dict['first_name'],
         result_dict['last_name'],
         result_dict["email"],
         result_dict["phone"],
         result_dict["city"],
         result_dict['state'],
         result_dict['org_id'],
         result_dict['active'],
         result_dict['user_id']])
    conn.commit()
    return jsonify('user updated')


if __name__ == "__main__":
    create_all()
    app.run(port="8086", host="0.0.0.0", debug=True)
