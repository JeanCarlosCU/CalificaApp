from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017")
db = client["gestion_escolar"]


@app.route("/")
def index():
    return redirect(url_for("ver_todo"))


@app.route("/dashboard")
def ver_todo():
    alumnos = list(db["alumnos"].find())
    maestros = list(db["maestros"].find())
    materias = list(db["materias"].find())
    return render_template("maestro.html", alumnos=alumnos, maestros=maestros, materias=materias)


@app.route("/agregar_alumno", methods=["POST"])
def agregar_alumno():
    db["alumnos"].insert_one({
        "nombre": request.form["nombre"],
        "matricula": request.form["matricula"]
    })
    return redirect(url_for("ver_todo"))


@app.route("/agregar_maestro", methods=["POST"])
def agregar_maestro():
    db["maestros"].insert_one({
        "nombre": request.form["nombre"],
        "especialidad": request.form["especialidad"]
    })
    return redirect(url_for("ver_todo"))


@app.route("/agregar_materia", methods=["POST"])
def agregar_materia():
    db["materias"].insert_one({
        "nombre": request.form["nombre"]
    })
    return redirect(url_for("ver_todo"))


@app.route("/eliminar_alumno/<id>")
def eliminar_alumno(id):
    db["alumnos"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("ver_todo"))


@app.route("/eliminar_maestro/<id>")
def eliminar_maestro(id):
    db["maestros"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("ver_todo"))


@app.route("/eliminar_materia/<id>")
def eliminar_materia(id):
    db["materias"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("ver_todo"))


if __name__ == "__main__":

        app.run(debug=True)