from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "clave_secreta"

clien = MongoClient("mongodb://localhost:27017")
db = clien["gestion_escolar"]

db["usuarios"].update_one(
    {"usuario": "admin"},
    {"$setOnInsert": {
        "usuario": "admin",
        "password": "1234",
        "rol": "maestro",
        "identificador": "ADMIN01",
        "foto": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQguFxMe9FNalCXJ9vcgb3OxoV_mf4TMp9XuwzS1QnCL1ctscveb99aO2k&s"
    }},
    upsert=True
)

@app.route("/")
def inicio():
    return redirect(url_for("login"))

@app.route("/registro", methods=["GET", "POST"])
def registro():
    mensaje = ""
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        rol = request.form["rol"]
        identificador = request.form.get("identificador")

        existe = db["usuarios"].find_one({"usuario": usuario})
        if existe:
            mensaje = "El usuario ya existe"
        else:
            db["usuarios"].insert_one({
                "usuario": usuario,
                "password": password,
                "rol": rol,
                "identificador": identificador,
                "foto": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQguFxMe9FNalCXJ9vcgb3OxoV_mf4TMp9XuwzS1QnCL1ctscveb99aO2k&s"
            })
            mensaje = "Registro exitoso."
    return render_template("registro.html", mensaje=mensaje)

@app.route("/login", methods = ["GET", "POST"])
def login():

    mensaje = ""

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        usuario_db = db["usuarios"].find_one({
            "usuario" : usuario,
            "password" : password
        })

        if usuario_db:
            session["usuario"] = usuario_db["usuario"]
            session["rol"] = usuario_db["rol"]
            session["identificador"] = usuario_db.get("identificador")

            if usuario_db["rol"] == "maestro":
                return redirect(url_for("Perfil_Maestro", nombre_maestro=usuario_db["usuario"].lower()))
            elif usuario_db["rol"] == "alumno":
                return redirect(url_for("Index_Alumnos"))
        else:

            mensaje = "Usuario o contraseña incorrecta"

    return render_template(
        "login.html",
        mensaje = mensaje
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/maestro/<nombre_maestro>")
def Perfil_Maestro(nombre_maestro):
    if "usuario" not in session or session["rol"] != "maestro":
        return "Acceso denegado.", 403

    maestro_info = db["usuarios"].find_one({"usuario": session["usuario"]})
    url_foto = maestro_info.get("foto", "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQguFxMe9FNalCXJ9vcgb3OxoV_mf4TMp9XuwzS1QnCL1ctscveb99aO2k&s")

    materias_db = db["maestros"].find({"nombre": nombre_maestro.capitalize()})
    # Corregido para que no se repita la misma materia si está duplicada en BD
    lista_materias = list(set([m["materia"] for m in materias_db]))
    if not lista_materias:
        lista_materias = ["Por asignar o Admin"]

    alumnos_profe = list(db["alumnos"].find({"maestro": nombre_maestro.capitalize()}))

    for alumno in alumnos_profe:
        calif_db = db["calificaciones"].find_one({
            "matricula_alumno": alumno["matricula"].strip(),
            "materia": alumno["materia"]
        })
        if calif_db:
            alumno["u1"] = calif_db.get("u1", "-")
            alumno["u2"] = calif_db.get("u2", "-")
            alumno["u3"] = calif_db.get("u3", "-")
            
            valores = []
            if isinstance(alumno["u1"], (int, float)): valores.append(alumno["u1"])
            if isinstance(alumno["u2"], (int, float)): valores.append(alumno["u2"])
            if isinstance(alumno["u3"], (int, float)): valores.append(alumno["u3"])
            
            if valores:
                alumno["resultado"] = round(sum(valores) / len(valores), 1)
            else:
                alumno["resultado"] = "-"
                
            alumno["id_calif"] = str(calif_db["_id"])
        else:
            alumno["u1"] = "-"
            alumno["u2"] = "-"
            alumno["u3"] = "-"
            alumno["resultado"] = "-"
            alumno["id_calif"] = None

    return render_template("maestro.html", alumnos=alumnos_profe, maestro=nombre_maestro.capitalize(), materias=lista_materias, foto=url_foto)

@app.route("/cambiar_foto", methods=["POST"])
def cambiar_foto():
    if "usuario" not in session:
        return redirect(url_for("login"))
    nueva_url = request.form.get("nueva_foto")
    db["usuarios"].update_one({"usuario": session["usuario"]}, {"$set": {"foto": nueva_url}})
    return redirect(url_for("Perfil_Maestro", nombre_maestro=session["usuario"].lower()))

@app.route("/alumnos")
def Index_Alumnos():
    if "usuario" not in session or session["rol"] != "alumno":
        return "Acceso denegado.", 403

    mis_inscripciones = list(db["alumnos"].find({"matricula": session["identificador"]}))

    for inscripcion in mis_inscripciones:
        calif_db = db["calificaciones"].find_one({
            "matricula_alumno": session["identificador"],
            "materia": inscripcion["materia"]
        })
        if calif_db:
            valores = []
            if "u1" in calif_db and isinstance(calif_db["u1"], (int, float)): valores.append(calif_db["u1"])
            if "u2" in calif_db and isinstance(calif_db["u2"], (int, float)): valores.append(calif_db["u2"])
            if "u3" in calif_db and isinstance(calif_db["u3"], (int, float)): valores.append(calif_db["u3"])
            if valores:
                inscripcion["promedio"] = round(sum(valores) / len(valores), 1)
            else:
                inscripcion["promedio"] = "-"
        else:
            inscripcion["promedio"] = "-"

    return render_template("index_alumnos.html", inscripciones=mis_inscripciones)

@app.route("/alumno/ver_maestro/<nombre_maestro>")
def Alumno_Ver_Maestro(nombre_maestro):
    if "usuario" not in session or session["rol"] != "alumno":
        return "Acceso denegado.", 403

    alumno_datos = db["alumnos"].find_one({"matricula": session["identificador"]})

    alumnos_profe = list(db["alumnos"].find({"maestro": nombre_maestro.capitalize()}))

    for alumno in alumnos_profe:
        calif_db = db["calificaciones"].find_one({
            "matricula_alumno": alumno["matricula"].strip(),
            "materia": alumno["materia"]
        })
        if calif_db:
            valores = []
            if "u1" in calif_db and isinstance(calif_db["u1"], (int, float)): valores.append(calif_db["u1"])
            if "u2" in calif_db and isinstance(calif_db["u2"], (int, float)): valores.append(calif_db["u2"])
            if "u3" in calif_db and isinstance(calif_db["u3"], (int, float)): valores.append(calif_db["u3"])
            if valores:
                alumno["nota"] = round(sum(valores) / len(valores), 1)
            else:
                alumno["nota"] = "-"
        else:
            alumno["nota"] = "-"

    return render_template("ver_maestro.html", alumnos=alumnos_profe, maestro=nombre_maestro.capitalize())

@app.route("/agregar_archivo")
def Agregar_Archivo():
    return render_template("agregar_archivo.html")

@app.route("/inicio_login")
def Inicio_de_sesion():
    return render_template("inicio_login.html")

@app.route("/añadir")
def añadir_documento():
      if "usuario" not in session or session["rol"] != "maestro":
            return "Solo los maestros pueden registrar datos.", 403
      return render_template("formulario.html")

@app.route("/guardar", methods=["POST"])
def guardar_datos():
      tipo = request.form.get('tipo_documento')

      nombre_usuario_sesion = session.get("usuario", "juan")

      if tipo == "alumno":
            materia_elegida = request.form.get("materia_alumno")
            maestro_assigned = db["maestros"].find_one({"materia": materia_elegida})

            if maestro_assigned:
                  nombre_profe = maestro_assigned["nombre"].capitalize()
            else:
                  nombre_profe = "Por asignar"

            datos_alumno = {
                  "nombre" : request.form.get("nombre_alumno"),
                  "matricula" : request.form.get("matricula").strip(),
                  "materia" : materia_elegida,
                  "maestro" : nombre_profe
            }
            db["alumnos"].insert_one(datos_alumno)
            print ("Alumno guardado con exito")
            return redirect(url_for("Perfil_Maestro", nombre_maestro=nombre_usuario_sesion.lower()))

      elif tipo == "maestro":
            datos_maestro = {
                  "nombre" : request.form.get("nombre_maestro").capitalize(),
                  "materia" : request.form.get("materia_maestro")
            }
            db["maestros"].insert_one(datos_maestro)
            print ("Maestro guardado con exito")
            return redirect(url_for("Perfil_Maestro", nombre_maestro=nombre_usuario_sesion.lower()))

      elif tipo == "materia":
            datos_materia = {"nombre_materia" : request.form.get("nombre_materia")}
            db["materias"].insert_one(datos_materia)
            print ("Materia guardada con exito")
            return redirect(url_for("Perfil_Maestro", nombre_maestro=nombre_usuario_sesion.lower()))

      elif tipo == "calificacion":
            mat_limpia = request.form.get("calif_matricula").strip()
            materia_calif = request.form.get("materia_calif")

            if not materia_calif:
                profe_db = db["maestros"].find_one({"nombre": nombre_usuario_sesion.capitalize()})
                materia_calif = profe_db["materia"] if profe_db else "Desconocida"

            datos_calificacion = {
                  "matricula_alumno" : mat_limpia,
                  "materia" : materia_calif
            }

            u1_val = request.form.get("u1")
            u2_val = request.form.get("u2")
            u3_val = request.form.get("u3")

            if u1_val and u1_val.strip() != "": datos_calificacion["u1"] = float(u1_val)
            if u2_val and u2_val.strip() != "": datos_calificacion["u2"] = float(u2_val)
            if u3_val and u3_val.strip() != "": datos_calificacion["u3"] = float(u3_val)

            db["calificaciones"].update_one(
                {"matricula_alumno": mat_limpia, "materia": materia_calif},
                {"$set": datos_calificacion},
                upsert=True
            )
            print ("Calificacion guardada con exito")
            return redirect(url_for("Perfil_Maestro", nombre_maestro=nombre_usuario_sesion.lower()))

      return redirect(url_for("Perfil_Maestro", nombre_maestro=nombre_usuario_sesion.lower()))

@app.route("/eliminar/alumno/<id_alumno>")
def eliminar_alumno(id_alumno):
    if "usuario" not in session or session["rol"] != "maestro":
        return "Acceso denegado.", 403
    db["alumnos"].delete_one({"_id": ObjectId(id_alumno)})
    print ("Alumno eliminado con exito")
    return redirect(url_for("Perfil_Maestro", nombre_maestro=session["usuario"].lower()))

@app.route("/eliminar/calificacion/<id_calif>")
def eliminar_calificacion(id_calif):
    if "usuario" not in session or session["rol"] != "maestro":
        return "Acceso denegado.", 403
    db["calificaciones"].delete_one({"_id": ObjectId(id_calif)})
    print ("Calificacion borrada con exito")
    return redirect(url_for("Perfil_Maestro", nombre_maestro=session["usuario"].lower()))

@app.route("/eliminar/maestro/<id_maestro>")
def eliminar_maestro(id_maestro):
    db["maestros"].delete_one({"_id": ObjectId(id_maestro)})
    print ("Docente eliminado")
    return redirect(url_for("inicio"))

@app.route("/eliminar/materia/<id_materia>")
def eliminar_materia(id_materia):
    db["materias"].delete_one({"_id": ObjectId(id_materia)})
    print ("Materia eliminada")
    return redirect(url_for("inicio"))

@app.route("/eliminar/inscripcion/<id_inscripcion>")
def eliminar_inscripcion(id_inscripcion):
    if "usuario" not in session or session["rol"] != "maestro":
        return "Acceso denegado.", 403
    db["alumnos"].delete_one({"_id": ObjectId(id_inscripcion)})
    print ("Materia del usuario eliminada con exito")
    return redirect(url_for("Perfil_Maestro", nombre_maestro=session["usuario"].lower()))

if __name__ == "__main__":

        app.run(debug=True)