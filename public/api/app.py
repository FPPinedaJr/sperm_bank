from flask import Flask, jsonify, request, make_response
from flask_mysqldb import MySQL
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from functools import wraps
import datetime

app = Flask(__name__)




# Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "spermbank"
app.config["JWT_SECRET_KEY"] = "your_origin@69"
app.config["JWT_ALGORITHM"] = "HS256"


mysql = MySQL(app)
jwt = JWTManager(app)




# Helper function
def fetch_data(query, args=()):
    cur = mysql.connection.cursor()
    cur.execute(query, args)
    data = cur.fetchall()
    cur.close()
    return data


def execute_query(query, args=()):
    cur = mysql.connection.cursor()
    cur.execute(query, args)
    mysql.connection.commit()
    cur.close()




# Authentication
@app.route("/api/test", methods=["GET"])
@jwt_required()
def test_jwt():
    identity = get_jwt_identity()
    return jsonify({"message": "Token is valid!", "user": identity}), 200


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    execute_query(
        """
        INSERT INTO users (username, password, role) 
        VALUES (%s, SHA2(%s, 256), %s)
        """,
        (data["username"], data["password"], data["role"]),
    )
    return jsonify({"message": "User registered successfully."}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    user = fetch_data(
        """
        SELECT * FROM users 
        WHERE username = %s AND password = SHA2(%s, 256)
        """,
        (data["username"], data["password"]),
    )
    if user:
        access_token = create_access_token(
            identity={"username": user[0][1], "role": user[0][3]},
            expires_delta=datetime.timedelta(hours=1),
        )
        return jsonify({"token": access_token}), 200
    return jsonify({"message": "Invalid credentials."}), 401


def role_required(required_role):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = get_jwt_identity()
            if user["role"] != required_role:
                return jsonify({"message": "Access forbidden."}), 403
            return func(*args, **kwargs)

        return wrapper

    return decorator




############################
##   E N D   P O I N T S  ##
############################

@app.route("/api/role_types", methods=["GET"])
@jwt_required()
def get_role_types():
    role_types = fetch_data("SELECT * FROM role_types")
    return jsonify(role_types), 200


@app.route("/api/role_types", methods=["POST"])
@role_required("admin")
def add_role_type():
    data = request.json
    execute_query(
        """
        INSERT INTO role_types (description) VALUES (%s)
        """,
        (data["description"],),
    )
    return jsonify({"message": "Role_type added successfully."}), 201


@app.route("/api/role_types/<int:role_type_id>", methods=["PUT"])
@role_required("admin")
def update_role_type(role_type_id):
    data = request.json
    execute_query(
        """
        UPDATE role_types SET description = %s WHERE idrole_types = %s
    """,
        (data["description"], role_type_id),
    )
    return jsonify({"message": "Role_type updated successfully."}), 200


@app.route("/api/role_types/<int:role_type_id>", methods=["DELETE"])
@role_required("admin")
def delete_role_type(role_type_id):
    execute_query("DELETE FROM role_types WHERE idrole_types = %s", (role_type_id,))
    return jsonify({"message": "Role_type deleted successfully."}), 200


if __name__ == "__main__":
    app.run(debug=True)