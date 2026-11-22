from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
import json
import os

app = Flask(__name__)

ARCHIVO = "datos.json"


def cargar_datos():
   if os.path.exists(ARCHIVO):
       with open(ARCHIVO, "r", encoding="utf-8") as f:
           return json.load(f)
   return []


def guardar_datos(datos):
   with open(ARCHIVO, "w", encoding="utf-8") as f:
       json.dump(datos, f, ensure_ascii=False, indent=4)


def nuevo_id(datos):
   if not datos:
       return 1
   return max(d["id"] for d in datos) + 1


def buscar_por_id(datos, id):
   for d in datos:
       if d["id"] == id:
           return d
   return None


@app.route("/")
def index():
   return render_template("index.html")


@app.route("/registrar", methods=["POST"])
def registrar():
   datos = cargar_datos()

   nombre = request.form.get("nombre", "").strip()
   edad_raw = request.form.get("edad", "").strip()
   correo = request.form.get("correo", "").strip()
   programa = request.form.get("programa", "").strip()

   errores = []

   if not nombre:
       errores.append("El nombre es obligatorio.")
   if not edad_raw:
       errores.append("La edad es obligatoria.")
   else:
       try:
           edad = int(edad_raw)
           if edad < 0 or edad > 120:
               errores.append("La edad debe estar entre 0 y 120 años.")
       except ValueError:
           errores.append("La edad debe ser un número entero.")
   if not correo:
       errores.append("El correo es obligatorio.")
   elif "@" not in correo or "." not in correo:
       errores.append("El correo no tiene un formato válido.")
   if not programa:
       errores.append("El programa es obligatorio.")

   if errores:
       return render_template("resultado.html", accion="error", errores=errores), 400

   nuevo = {
       "id": nuevo_id(datos),
       "nombre": nombre,
       "edad": int(edad_raw),
       "correo": correo,
       "programa": programa
   }
   datos.append(nuevo)
   guardar_datos(datos)

   return render_template("resultado.html", accion="registrado", estudiante=nuevo)


@app.route("/estudiantes")
def listar():
   datos = cargar_datos()
   total = len(datos)
   promedio = (sum(d["edad"] for d in datos) / total) if total else 0
   return render_template(
       "lista.html",
       estudiantes=datos,
       total=total,
       promedio=round(promedio, 1)
   )


@app.route("/estudiante/<int:id>")
def detalle(id):
   datos = cargar_datos()
   estudiante = buscar_por_id(datos, id)
   if estudiante is None:
       abort(404)
   return render_template("detalle.html", estudiante=estudiante)


@app.route("/editar/<int:id>")
def editar(id):
   datos = cargar_datos()
   estudiante = buscar_por_id(datos, id)
   if estudiante is None:
       abort(404)
   return render_template("editar.html", estudiante=estudiante)


@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar(id):
   datos = cargar_datos()
   estudiante = buscar_por_id(datos, id)
   if estudiante is None:
       abort(404)

   nombre = request.form.get("nombre", "").strip()
   edad_raw = request.form.get("edad", "").strip()
   correo = request.form.get("correo", "").strip()
   programa = request.form.get("programa", "").strip()

   errores = []

   if not nombre:
       errores.append("El nombre es obligatorio.")
   if not edad_raw:
       errores.append("La edad es obligatoria.")
   else:
       try:
           edad = int(edad_raw)
           if edad < 0 or edad > 120:
               errores.append("La edad debe estar entre 0 y 120 años.")
       except ValueError:
           errores.append("La edad debe ser un número entero.")
   if not correo:
       errores.append("El correo es obligatorio.")
   elif "@" not in correo or "." not in correo:
       errores.append("El correo no tiene un formato válido.")
   if not programa:
       errores.append("El programa es obligatorio.")

   if errores:
       return render_template("resultado.html", accion="error", errores=errores), 400

   estudiante["nombre"] = nombre
   estudiante["edad"] = int(edad_raw)
   estudiante["correo"] = correo
   estudiante["programa"] = programa

   guardar_datos(datos)
   return render_template("resultado.html", accion="actualizado", estudiante=estudiante)


@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
   datos = cargar_datos()
   datos = [d for d in datos if d["id"] != id]
   guardar_datos(datos)
   return redirect(url_for("listar"))


@app.route("/api/estudiantes")
def api_estudiantes():
   return jsonify(cargar_datos())


@app.errorhandler(404)
def no_encontrado(error):
   return render_template("error.html", codigo=404, mensaje="Recurso no encontrado"), 404


@app.errorhandler(500)
def error_interno(error):
   return render_template("error.html", codigo=500, mensaje="Error interno del servidor"), 500


if __name__ == "__main__":
   app.run(debug=True)