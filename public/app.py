from flask import Flask, jsonify, request, make_response, render_template
from flask_mysqldb import MySQL
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from functools import wraps
import datetime
import MySQLdb.cursors

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



@app.route("/")
def show_sign_in():
    return render_template("authentication.html")

@app.route("/individuals")
def show_individuals():
    return render_template("individuals.html")



# Helper function
def fetch_data(query, args=()):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
            identity={"username": user[0]["username"], "role": user[0]["role"]},
            expires_delta=datetime.timedelta(hours=5),
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



# ROLE_TYPES
@app.route("/api/role_types", methods=["GET"])
@jwt_required()
def get_role_types():
    role_types = fetch_data("SELECT * FROM role_types")
    return jsonify(role_types), 200


@app.route("/api/role_types/<int:role_type_id>", methods=["GET"])
@jwt_required()
def search_role_types(role_type_id):
    role_types = fetch_data("SELECT * FROM role_types WHERE idrole_types= %s", (role_type_id,))
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



# RELATIONSHIP_TYPES
@app.route("/api/relationship_types", methods=["GET"])
@jwt_required()
def get_relationship_types():
    relationship_types = fetch_data("SELECT * FROM relationship_types")
    return jsonify(relationship_types), 200


@app.route("/api/relationship_types/<int:relationship_id>", methods=["GET"])
@jwt_required()
def search_relationship_types(relationship_id):
    relationship_types = fetch_data("SELECT * FROM relationship_types WHERE idrelationship_types= %s", (relationship_id,))
    return jsonify(relationship_types), 200


@app.route("/api/relationship_types", methods=["POST"])
@role_required("admin")
def add_relationship_type():
    data = request.json
    execute_query(
        """
        INSERT INTO relationship_types (description) VALUES (%s)
        """,
        (data["description"],),
    )
    return jsonify({"message": "Relationship_type added successfully."}), 201


@app.route("/api/relationship_types/<int:relationship_type_id>", methods=["PUT"])
@role_required("admin")
def update_relationship_type(relationship_type_id):
    data = request.json
    execute_query(
        """
        UPDATE relationship_types SET description = %s WHERE idrelationship_types = %s
        """,
        (data["description"], relationship_type_id),
    )
    return jsonify({"message": "Relationship_type updated successfully."}), 200


@app.route("/api/relationship_types/<int:relationship_type_id>", methods=["DELETE"])
@role_required("admin")
def delete_relationship_type(relationship_type_id):
    execute_query("DELETE FROM relationship_types WHERE idrelationship_types = %s", (relationship_type_id,))
    return jsonify({"message": "Relationship_type deleted successfully."}), 200



# DONATIONS
@app.route("/api/donations", methods=["GET"])
@jwt_required()
def get_donations():
    donations = fetch_data("SELECT * FROM donations")
    return jsonify(donations), 200


@app.route("/api/donations/<int:donation_id>", methods=["GET"])
@jwt_required()
def search_donations(donation_id):
    donations = fetch_data("SELECT * FROM donations WHERE iddonations= %s", (donation_id,))
    return jsonify(donations), 200


@app.route("/api/donations", methods=["POST"])
@role_required("admin")
def add_donation():
    data = request.json
    execute_query(
        """
        INSERT INTO donations (individual_id, date, ampoule_count, motilitiy_rating) VALUES (%s, %s, %s, %s)
        """,
        (data["individual_id"], data["date"], data["ampoule_count"], data["motilitiy_rating"]),
    )
    return jsonify({"message": "Donation added successfully."}), 201


@app.route("/api/donations/<int:donation_id>", methods=["PUT"])
@role_required("admin")
def update_donation(donation_id):
    data = request.json
    execute_query(
        """
        UPDATE donations SET individual_id = %s, date = %s, ampoule_count = %s, motilitiy_rating = %s WHERE iddonations = %s
        """,
        (data["individual_id"], data["date"], data["ampoule_count"], data["motilitiy_rating"], donation_id),
    )
    return jsonify({"message": "Donation updated successfully."}), 200


@app.route("/api/donations/<int:donation_id>", methods=["DELETE"])
@role_required("admin")
def delete_donation(donation_id):
    execute_query("DELETE FROM donations WHERE iddonations = %s", (donation_id,))
    return jsonify({"message": "Donation deleted successfully."}), 200



# INDIVIDUALS
@app.route("/api/individuals", methods=["GET"])
@jwt_required()
def get_individuals():
    individuals = fetch_data("SELECT * FROM individuals")
    return jsonify(individuals), 200


@app.route("/api/individuals/<int:individual_id>", methods=["GET"])
@jwt_required()
def search_individuals(individual_id):
    individuals = fetch_data("SELECT * FROM individuals WHERE idindividuals= %s", (individual_id,))
    return jsonify(individuals), 200


@app.route("/api/individuals", methods=["POST"])
@role_required("admin")
def add_individual():
    data = request.json
    print(data)
    execute_query(
        """
        INSERT INTO individuals (type_id, birthdate, is_male, fname, mname, lname, address, contact) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (data["type_id"], data["birthdate"], data["is_male"], data["fname"], 
         data["mname"], data["lname"], data["address"], data["contact"]),
    )
    return jsonify({"message": "Individual added successfully."}), 201


@app.route("/api/individuals/<int:individual_id>", methods=["PUT"])
@role_required("admin")
def update_individual(individual_id):
    data = request.json
    execute_query(
        """
        UPDATE individuals SET 
        type_id = %s, birthdate = %s, is_male = %s, fname = %s,
        mname = %s, lname = %s, address = %s, contact = %s WHERE idindividuals = %s
        """,
        (data["type_id"], data["birthdate"], data["is_male"], data["fname"], 
        data["mname"], data["lname"], data["address"], data["contact"], individual_id),
    )
    return jsonify({"message": "Individual updated successfully."}), 200


@app.route("/api/individuals/<int:individual_id>", methods=["DELETE"])
@role_required("admin")
def delete_individual(individual_id):
    execute_query("DELETE FROM individuals WHERE idindividuals = %s", (individual_id,))
    return jsonify({"message": "Individual deleted successfully."}), 200



# RELATIONSHIPS
@app.route("/api/relationships", methods=["GET"])
@jwt_required()
def get_relationships():
    relationships = fetch_data("SELECT * FROM relationships")
    return jsonify(relationships), 200

@app.route("/api/relationships/<int:relationship_id>", methods=["GET"])
@jwt_required()
def search_relationships(relationship_id):
    relationships = fetch_data("SELECT * FROM relationships WHERE idrelationships= %s", (relationship_id,))
    return jsonify(relationships), 200

@app.route("/api/relationships", methods=["POST"])
@role_required("admin")
def add_relationship():
    data = request.json
    execute_query(
        """
        INSERT INTO relationships (type_id, individual_1_id, individual_2_id, date_start, date_end) VALUES (%s, %s, %s, %s, %s)
        """,
        (data["type_id"], data["individual_1_id"], data["individual_2_id"], data["date_start"], data["date_end"]),
    )
    return jsonify({"message": "Relationship added successfully."}), 201


@app.route("/api/relationships/<int:relationship_id>", methods=["PUT"])
@role_required("admin")
def update_relationship(relationship_id):
    data = request.json
    execute_query(
        """
        UPDATE relationships SET 
        type_id = %s, individual_1_id = %s, individual_2_id = %s, date_start = %s, date_end = %s WHERE idrelationships = %s
        """,
        (data["type_id"], data["individual_1_id"], data["individual_2_id"], data["date_start"], data["date_end"], relationship_id),
    )
    return jsonify({"message": "Relationship updated successfully."}), 200


@app.route("/api/relationships/<int:relationship_id>", methods=["DELETE"])
@role_required("admin")
def delete_relationship(relationship_id):
    execute_query("DELETE FROM relationships WHERE idrelationships = %s", (relationship_id,))
    return jsonify({"message": "Relationship deleted successfully."}), 200



if __name__ == "__main__":
    app.run(debug=True)
