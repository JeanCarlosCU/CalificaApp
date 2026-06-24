from flask import Flask, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from database import get_db
from email_validator import validate_email, EmailNotValidError
from datetime import datetime

def es_correo_valido(email):
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False

app = Flask(__name__)
app.secret_key = "clave_secreta"
db = get_db()

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/alumnos", methods=["GET", "POST"])
def alumnos():
    edit_id = request.args.get('edit_id')
    alumno_edit = db["alumnos"].find_one({"_id": ObjectId(edit_id)}) if edit_id else None
    if request.method == "POST":
        if edit_id:
            db["alumnos"].update_one({"_id": ObjectId(edit_id)}, {"$set": request.form.to_dict()})
        else:
            db["alumnos"].insert_one(request.form.to_dict())
        return redirect(url_for("alumnos"))
    return render_template("alumnos.html", lista=list(db["alumnos"].find()), alumno_edit=alumno_edit)

@app.route("/agregar_alumno", methods=["POST"])
def agregar_alumno():
    db["alumnos"].insert_one(request.form.to_dict())
    return redirect(url_for("alumnos"))

@app.route("/eliminar_alumno/<id>")
def eliminar_alumno(id):
    db["alumnos"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("alumnos"))


@app.route("/maestros", methods=["GET", "POST"])
def maestros():
    edit_id = request.args.get('edit_id')
    maestro_edit = db["maestros"].find_one({"_id": ObjectId(edit_id)}) if edit_id else None
    if request.method == "POST":
        if edit_id:
            db["maestros"].update_one({"_id": ObjectId(edit_id)}, {"$set": request.form.to_dict()})
        else:
            db["maestros"].insert_one(request.form.to_dict())
        return redirect(url_for("maestros"))
    return render_template("maestros.html", lista=list(db["maestros"].find()), maestro_edit=maestro_edit)

@app.route("/agregar_maestro", methods=["POST"])
def agregar_maestro():
    db["maestros"].insert_one(request.form.to_dict())
    return redirect(url_for("maestros"))

@app.route("/eliminar_maestro/<id>")
def eliminar_maestro(id):
    db["maestros"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("maestros"))


@app.route("/materias", methods=["GET", "POST"])
def materias():
    edit_id = request.args.get('edit_id')
    materia_edit = db["materias"].find_one({"_id": ObjectId(edit_id)}) if edit_id else None
    if request.method == "POST":
        if edit_id:
            db["materias"].update_one({"_id": ObjectId(edit_id)}, {"$set": request.form.to_dict()})
        else:
            db["materias"].insert_one(request.form.to_dict())
        return redirect(url_for("materias"))
    return render_template("materias.html", lista=list(db["materias"].find()), materia_edit=materia_edit)

@app.route("/agregar_materia", methods=["POST"])
def agregar_materia():
    db["materias"].insert_one(request.form.to_dict())
    return redirect(url_for("materias"))

@app.route("/eliminar_materia/<id>")
def eliminar_materia(id):
    db["materias"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("materias"))

@app.route("/grupos", methods=["GET", "POST"])
def grupos():
    edit_id = request.args.get('edit_id')
    grupo_edit = db["grupos"].find_one({"_id": ObjectId(edit_id)}) if edit_id else None
    if request.method == "POST":
        if edit_id:
            db["grupos"].update_one({"_id": ObjectId(edit_id)}, {"$set": request.form.to_dict()})
        else:
            db["grupos"].insert_one(request.form.to_dict())
        return redirect(url_for("grupos"))
    return render_template("grupos.html", lista=list(db["grupos"].find()), maestros=list(db["maestros"].find()), grupo_edit=grupo_edit)

@app.route("/eliminar_grupo/<id>")
def eliminar_grupo(id):
    db["grupos"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("grupos"))

if __name__ == "__main__":
    app.run(debug=True)