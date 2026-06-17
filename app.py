from flask import Flask, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from database import get_db

app = Flask(__name__)
app.secret_key = "clave_secreta"
db = get_db()

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/alumnos")
def alumnos():
    return render_template("alumnos.html", lista=list(db["alumnos"].find()))

@app.route("/agregar_alumno", methods=["POST"])
def agregar_alumno():
    if not request.form.get("matricula"):
        flash("Error: La matrícula es obligatoria")
        return redirect(url_for("alumnos"))
    db["alumnos"].insert_one(request.form.to_dict())
    flash("Alumno registrado correctamente")
    return redirect(url_for("alumnos"))

@app.route("/eliminar_alumno/<id>")
def eliminar_alumno(id):
    db["alumnos"].delete_one({"_id": ObjectId(id)})
    flash("Alumno eliminado")
    return redirect(url_for("alumnos"))


@app.route("/maestros")
def maestros():
    return render_template("maestros.html", lista=list(db["maestros"].find()))

@app.route("/agregar_maestro", methods=["POST"])
def agregar_maestro():
    if not request.form.get("num_empleado"):
        flash("Error: El número de empleado es obligatorio")
        return redirect(url_for("maestros"))
    db["maestros"].insert_one(request.form.to_dict())
    flash("Maestro registrado")
    return redirect(url_for("maestros"))

@app.route("/eliminar_maestro/<id>")
def eliminar_maestro(id):
    db["maestros"].delete_one({"_id": ObjectId(id)})
    flash("Maestro eliminado")
    return redirect(url_for("maestros"))

@app.route("/materias")
def materias():
    return render_template("materias.html", lista=list(db["materias"].find()))

@app.route("/agregar_materia", methods=["POST"])
def agregar_materia():
    db["materias"].insert_one(request.form.to_dict())
    flash("Materia registrada")
    return redirect(url_for("materias"))

@app.route("/eliminar_materia/<id>")
def eliminar_materia(id):
    db["materias"].delete_one({"_id": ObjectId(id)})
    flash("Materia eliminada")
    return redirect(url_for("materias"))

if __name__ == "__main__":
    app.run(debug=True)