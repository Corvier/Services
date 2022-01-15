import os

from werkzeug.security import check_password_hash, generate_password_hash
from flask import render_template, request, redirect, url_for, flash
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
from flask_mail import Mail, Message # Importando libreria para enviar correos --AGREGUE ESTO--

app = Flask(__name__)

# Configuracion de correo electronico
app.config["MAIL_SERVER"] = os.getenv('MAIL_SERVER')
app.config["MAIL_PORT"] = int(os.getenv('MAIL_PORT')) or 587
app.config["MAIL_USE_TLS"] = os.getenv('MAIL_USE_TLS')
app.config["MAIL_USERNAME"] = os.getenv('MAIL_USERNAME')
app.config["MAIL_PASSWORD"] = os.getenv('MAIL_PASSWORD')

print(f"\n\n{os.getenv('MAIL_PORT')}")

mail = Mail(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Check for environment variable
if not os.getenv("DB_URL"):
    raise RuntimeError("DB_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DB_URL"))
db = scoped_session(sessionmaker(bind=engine))

# funcion para cargar datos en el index
def load_index():
    dataUser = db.execute("SELECT * FROM users WHERE user_id = :id", {"id": session["user_id"]}).fetchone()
    session["administrador"] = dataUser["administrador"]
    
    dataBusiness = db.execute("SELECT * FROM businesses").fetchall()
    
    dataBusinessUser = db.execute("SELECT * FROM businesses WHERE user_id = :id", {"id": session["user_id"]}).fetchall()
    
    dataCategory = db.execute("SELECT category_id, category FROM business_category").fetchall()

    dataLocation = db.execute("SELECT * FROM locations").fetchall()

    if session['administrador'] is 1:
        print("\n\n\nEs admin admin :D\n\n")
        dataBusinessUserID = db.execute("SELECT business_id FROM businesses WHERE user_id = :id", {"id": session["user_id"]}).fetchall()
        # Guardo el business_id en una variable de sesion
        session["business_id"] = dataBusinessUserID[0]["business_id"]
    else:
        session["business_id"] = 0
    
    print(f"\n\nVariables en session. {session}")
    
    context = {
        "dataUser": dataUser,
        "photoUser": dataUser['photo'],
        "dataBusiness": dataBusiness,
        "dataCategory": dataCategory,
        "dataLocation": dataLocation,
        "dataBusinessUser": dataBusinessUser,
    }
    return context


def load_products():
    dataProducts = db.execute("SELECT * FROM products WHERE business_id = :id", {"id": session["business_id"]}).fetchall()

    announce = db.execute("SELECT * FROM announcements").fetchall()

    dataProductsAll = db.execute("SELECT * FROM products").fetchall()

    context = {
        "dataProducts": dataProducts,
        "announce": announce,
        "dataProductsAll": dataProductsAll, # En productos
    }

    return context


@app.route("/")
def main():
    if "user_id" in session:
        return render_template("home.html")
    else:
        return render_template("home.html")


# Route inicio
@app.route("/inicio", methods=["GET", "POST"])
def inicio():
    if "user_id" in session:
        context = load_index()
        return render_template("index.html", context=context)
    else:
        return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("inicio"))
        else:
            return render_template("register.html")
        
    elif request.method == "POST":
        username = request.form.get("username")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        direccion = request.form.get("direccion")
        imagen = request.form.get("imagen")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Contexto de los datos
        context = {
            "username": username,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "direccion": direccion,
            "imagen": imagen,
            "password": password,
            "confirmation": confirmation,
        }

        print(f"\n\n{context}\n\n")

        if not username or not last_name or not email or not phone or not direccion or not password or not confirmation:
            flash("Por favor rellena todos los campos.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639678645/gykhoa7pa3q25fp6ax7s.png")
            # return render_template("register.html", **context)
            return redirect(url_for("register"))
        
        if password != confirmation:
            flash("Las contraseñas no coinciden.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
            return redirect(url_for("register"))

        if db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).rowcount != 0:
            flash("El Email ya esta registrado.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
            return redirect(url_for("register"))

        password_encriptado = generate_password_hash(password)

        if imagen:
            db.execute("INSERT INTO users (username, last_name, email, pass_hash, direction, phone, photo) \
                    VALUES (:username, :last_name, :email, :pass_hash, :direction, :phone, :photo)", \
                    {"username": username, "last_name": last_name, "email": email, "pass_hash": password_encriptado, "direction": direccion, "phone": phone, "photo": imagen})
        
        else:
            db.execute("INSERT INTO users (username, last_name, email, pass_hash, direction, phone) \
                    VALUES (:username, :last_name, :email, :pass_hash, :direction, :phone)", \
                    {"username": username, "last_name": last_name, "email": email, "pass_hash": password_encriptado, "direction": direccion, "phone": phone})
        
        db.commit()
        
        flash("Registro exitoso.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")
        return redirect(url_for("login"))

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("inicio"))
        else:
            return render_template("login.html")

    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            # Warning
            flash("Por favor rellena todos los campos.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639678645/gykhoa7pa3q25fp6ax7s.png")
            return redirect(url_for("login"))

        sQuery = "SELECT * FROM users WHERE email = :email"

        dataUser = db.execute(sQuery, {"email": email}).fetchone()

        print(f"\n\nel squery: {dataUser}\n\n")

        if dataUser is None:
            flash("El correo electrónico no existe!!.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
            return redirect(url_for("login"))

        # Validar contraseña
        if not check_password_hash(dataUser['pass_hash'], password):
            flash("Contraseña o correo incorrecto / Veficar mayúsculas.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
            return redirect(url_for("login"))

        # Guardar datos de usuario en la sesion
        session['username'] = dataUser['username']
        session["user_id"] = dataUser['user_id']
        session["administrador"] = dataUser['administrador']

        # Redireccionar a la pagina principal
        return redirect(url_for("inicio"))

    else:
        return render_template("login.html")


@app.route("/registerbusiness", methods=["GET", "POST"])
def register_business():
    if request.method == "GET":
        if "user_id" in session:
            return render_template("register_business.html")
        else:
            return render_template("login.html")
        
    elif request.method == "POST":
        administrador = request.form.get("administrador")
        business_name = request.form.get("business_name")
        phone = request.form.get("phone")
        direccion = request.form.get("direccion")
        categorias = int(request.form.get("categorias"))
        imagen = request.form.get("imagen")
        ampmStart = request.form.get("ampmStart")
        ampmEnd = request.form.get("ampmEnd")
        descripcion = request.form.get("descripcion")

        context = {
            "administrador": administrador,
            "business_name": business_name,
            "phone": phone,
            "direccion": direccion,
            "categorias": categorias,
            "imagen": imagen,
            "ampmStart": ampmStart,
            "ampmEnd": ampmEnd,
            "descripcion": descripcion,
        }

        print(f"\n\n{context}\n\n")

        if not administrador or not business_name or not phone or not direccion or not categorias or not imagen or not ampmStart or not ampmEnd or not descripcion:
            flash("Por favor rellena todos los campos.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639678645/gykhoa7pa3q25fp6ax7s.png")
            return redirect(url_for("register_business"))

        if imagen:
            db.execute("INSERT INTO businesses (user_id, category_id, business_name, direction, phone, startime, endtime, description, photo) \
                VALUES (:user_id, :category_id, :business_name, :direction, :phone, :startime, :endtime, :description, :photo)", \
                    {"user_id": session["user_id"], "category_id": categorias, "business_name": business_name, "direction": direccion, "phone": phone, "startime": ampmStart, "endtime": ampmEnd, "description": descripcion, "photo": imagen})
            
            db.execute("UPDATE users SET administrador = :administrador WHERE user_id = :user_id", {"administrador": administrador, "user_id": session["user_id"]})
        
        else:
            db.execute("INSERT INTO businesses (user_id, category_id, business_name, direction, phone, startime, endtime, description) \
                VALUES (:user_id, :category_id, :business_name, :direction, :phone, :startime, :endtime, :description)", \
                    {"user_id": session["user_id"], "category_id": categorias, "business_name": business_name, "direction": direccion, "phone": phone, "startime": ampmStart, "endtime": ampmEnd, "description": descripcion})
            
        db.commit()

        flash("¡Felicidades! Registro exitoso de tu negocio", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")
        return redirect(url_for("inicio"))


# Ruta para realizar pedidos y mostrar el detalle de los mismos
@app.route("/products/<business_id>", methods=["GET", "POST"])
def productos(business_id):
    if request.method == "GET":
        if "user_id" in session:

            context = load_products()
            dataBusiness = db.execute("SELECT * FROM businesses WHERE business_id = :business_id", {"business_id": business_id}).fetchall()

            dataReview = db.execute("SELECT username, review, score FROM users JOIN reviews ON users.user_id = reviews.user_id WHERE business_id =:business_id", {"business_id": business_id}).fetchall()
            
            return render_template("productos.html", context=context, dataBusiness=dataBusiness, dataReview=dataReview)
        else:
            return render_template("login.html")

    elif request.method == "POST":
        review = request.form.get("review")
        score = request.form.get("estrellas")

        context = {
            "review": review,
            "score": score
        }

        if "user_id" in session:
            # Consulta para obtener el id de mi tabla businesses
            dataBusiness = db.execute("SELECT * FROM businesses WHERE business_id = :business_id", {"business_id": business_id}).fetchall()
            # Consulta para obtener el id de mi tabla users
            dataUser = db.execute("SELECT * FROM users WHERE user_id = :user_id", {"user_id": session["user_id"]}).fetchall()

            # Validar datos de entrada
            if not review or not score:
                flash("Por favor rellena todos los campos.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639678645/gykhoa7pa3q25fp6ax7s.png")
                return redirect(url_for("productos", business_id=business_id))

            # Insertar criticas en la base de datos
            db.execute("INSERT INTO reviews (user_id, business_id, review, score) \
                VALUES (:user_id, :business_id, :review, :score)", \
                    {"user_id": session["user_id"], "business_id": business_id, "review": review, "score": score})

            # Guardar cambios en la base de datos
            db.commit()

            # Redireccionar a la pagina de inicio
            flash("¡Felicidades! ¡Gracias por tu comentario!", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")
            return redirect(url_for("productos", business_id=business_id))

        return context


@app.route("/admin", methods=["GET", "POST"])
def administration():
    if request.method == "GET":
        if "user_id" in session:
            context = load_products()

            context2 = load_index()

            return render_template("admin.html", productsAdmin=context, business=context2)
        else:
            return render_template("login.html")


@app.route("/admin/add_products", methods=["GET", "POST"])
def insertar():
    if request.method == "GET":
        if "user_id" in session:

            context = load_products()
            context2 = load_index()

            return render_template("admin.html", productsAdmin=context, business=context2)
        else:
            return render_template("login.html")
        
    elif request.method == "POST":
        # TODO
        # Obetener datos de la solicitud
        productName = request.form.get("productName")
        productCategory = request.form.get("productCategory")
        productDescripcion = request.form.get("productDescripcion")
        productImagen = request.form.get("productImagen")
        productFecha = request.form.get("productFecha")
        productStock = request.form.get("productStock")
        productUnitPrecio = request.form.get("productUnitPrecio")
        productBoxPrecio = request.form.get("productBoxPrecio")

        # Contexto de los datos
        context = {
            "productName": productName,
            "productCategory": productCategory,
            "productDescripcion": productDescripcion,
            "productImagen": productImagen,
            "productFecha": productFecha,
            "productStock": productStock,
            "productUnitPrecio": productUnitPrecio,
            "productBoxPrecio": productBoxPrecio,
        }

        print(f"\n\n{context}\n\n")

        if not productName or not productCategory or not productDescripcion or not productImagen or not productFecha or not productStock or not productUnitPrecio or not productBoxPrecio:
            flash("Por favor rellena todos los campos.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639678645/gykhoa7pa3q25fp6ax7s.png")
            return redirect(url_for("insertar"))

        if productImagen:
            db.execute("INSERT INTO products (business_id, product_name, category_id, description, photo, expiration_date, stock, unit_price, box_price) \
                VALUES (:business_id, :product_name, :category_id, :description, :photo, :expiration_date, :stock, :unit_price, :box_price)", \
                    {"business_id": session["business_id"], "product_name": productName, "category_id": productCategory, "description": productDescripcion, "photo": productImagen, "expiration_date": productFecha, "stock": productStock, "unit_price": productUnitPrecio, "box_price": productBoxPrecio})
            
        else:
            db.execute("INSERT INTO products (business_id, product_name, category_id, description, expiration_date, stock, unit_price, box_price) \
                VALUES (:business_id, :product_name, :category_id, :description, :expiration_date, :stock, :unit_price, box_price)", \
                    {"business_id": session["business_id"], "product_name": productName, "category_id": productCategory, "description": productDescripcion, "expiration_date": productFecha, "stock": productStock, "unit_price": productUnitPrecio, "box_price": productBoxPrecio})


        db.commit()
        
        flash("¡El producto se registro correctamente!", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")

        context = load_products()
        context2 = load_index()
        
        return render_template("admin.html", productsAdmin=context, business=context2)


@app.route("/admin/update_products/<product_id>", methods=["GET", "POST"])
def actualizar(product_id):
    if request.method == "GET":
        if "user_id" in session:
            context = load_products()
            context2 = load_index()
            
            return render_template("admin.html", productsAdmin=context, business=context2)
        else:
            return render_template("login.html")
        
    elif request.method == "POST":
        productName = request.form.get("productName")
        productCategory = request.form.get("productCategory")
        productDescripcion = request.form.get("productDescripcion")
        productFecha = request.form.get("productFecha")
        productStock = request.form.get("productStock")
        productUnitPrecio = request.form.get("productUnitPrecio")
        productBoxPrecio = request.form.get("productBoxPrecio")

        # Contexto de los datos
        context = {
            "productName": productName,
            "productCategory": productCategory,
            "productDescripcion": productDescripcion,
            "productFecha": productFecha,
            "productStock": productStock,
            "productUnitPrecio": productUnitPrecio,
            "productBoxPrecio": productBoxPrecio
        }

        print(f"\n\n{context}\n\n")

        if not productName or not productCategory or not productDescripcion or not productFecha or not productStock or not productUnitPrecio or not productBoxPrecio:
            flash("Por favor rellena todos los campos.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639678645/gykhoa7pa3q25fp6ax7s.png")
            return redirect(url_for("actualizar", product_id=product_id))
        
        db.execute("UPDATE products SET product_name = :product_name, category_id = :category_id, description = :description, expiration_date = :expiration_date, stock = :stock, unit_price = :unit_price, box_price = :box_price WHERE product_id = :product_id", \
            {"product_name": productName, "category_id": productCategory, "description": productDescripcion, "expiration_date": productFecha, "stock": productStock, "unit_price": productUnitPrecio, "box_price": productBoxPrecio, "product_id": product_id})

        db.commit()
        
        flash("¡El producto se actualizo correctamente!", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")

        context = load_products()
        context2 = load_index()
        
        return render_template("admin.html", productsAdmin=context, business=context2)


@app.route("/admin/delete_products/<product_id>", methods=["GET", "POST"])
def eliminar(product_id):
    if request.method == "GET":
        if "user_id" in session:
            db.execute("DELETE FROM products WHERE product_id = :product_id", {"product_id": product_id})
            db.commit()

            context = load_products()
            context2 = load_index()
            flash("¡Registro eliminado satisfactoriamente!.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")
            return render_template("admin.html", productsAdmin=context, business=context2)
        else:
            return redirect(url_for("login"))
        
    else:
        return redirect(url_for("admin"))


@app.route("/admin/announcements/<business_id>", methods=["GET", "POST"])
def anuncios(business_id):
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("administration"))
        else:
            return render_template("login.html")
        
    elif request.method == "POST":
        # TODO
        nameAnnoun = request.form.get("nameAnnoun")
        markAnnoun = request.form.get("markAnnoun")
        descriptionAnnoun = request.form.get("descriptionAnnoun")
        priceAnnoun = request.form.get("priceAnnoun")
        fechaAnnoun = request.form.get("fechaAnnoun")

        context = {
            "id_Business": business_id,
            "nameAnnoun": nameAnnoun,
            "markAnnoun": markAnnoun,
            "descriptionAnnoun": descriptionAnnoun,
            "priceAnnoun": priceAnnoun,
            "fechaAnnoun": fechaAnnoun
        }

        if not nameAnnoun or not markAnnoun or not descriptionAnnoun or not priceAnnoun or not fechaAnnoun:
            flash("Por favor rellena todos los campos.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639678645/gykhoa7pa3q25fp6ax7s.png")
            return redirect(url_for("anuncios", business_id=business_id))
        
        if db.execute("SELECT * FROM announcements WHERE business_id = :business_id", {"business_id": business_id}).rowcount == 0:

            db.execute("INSERT INTO announcements (business_id, product_name, mark, description, price, expiration_date) \
                VALUES (:business_id, :announcement_name, :mark, :description, :price, :announcement_date)", \
                    {"business_id": business_id, "announcement_name": nameAnnoun, "mark": markAnnoun, "description": descriptionAnnoun, "price": priceAnnoun, "announcement_date": fechaAnnoun})
            
            db.commit()
        
            flash("¡El anuncio se registro correctamente!", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")

            return redirect(url_for("administration"))

        else:
            db.execute("UPDATE announcements SET product_name = :product_name, mark = :mark, description = :description, price = :price, expiration_date = :expiration_date WHERE business_id = :business_id", \
                {"product_name": nameAnnoun, "mark": markAnnoun, "description": descriptionAnnoun, "price": priceAnnoun, "expiration_date": fechaAnnoun, "business_id": business_id})

            db.commit()
            
            flash("¡El anuncio se actualizo correctamente!", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")

            return redirect(url_for("administration"))


@app.route("/configuraciones", methods=["GET", "POST"])
def configuraciones():
    if request.method == "GET":
        if "user_id" in session:
            context = load_index()

            return render_template("settings.html", user=context)
        else:
            return render_template("login.html")
        
    elif request.method == "POST":
        if "user_id" in session:
            # Obtener los datos que llegan desde el formulario en user en stting.html
            username = request.form.get("username")
            email = request.form.get("email")
            phone = request.form.get("phone")
            direccion = request.form.get("direccion")
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")
            imagen = request.form.get("imagen")

            # Obtener los datos que llegan desde el formulario en business en stting.html
            business_name = request.form.get("business_name")
            business_direccion = request.form.get("business_direccion")
            business_phone = request.form.get("business_phone")
            business_descripcion = request.form.get("business_descripcion")
            ampmStart = request.form.get("ampmStart")
            ampmEnd = request.form.get("ampmEnd")
            imagen2 = request.form.get("imagen2")

            if username or email or phone or direccion or password or confirmation: 
                if password != confirmation:
                    flash("Las contraseñas no coinciden.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
                    return redirect(url_for("configuraciones"))
                
                # Generar contraseña encriptada
                password_encriptado = generate_password_hash(password)

                if imagen:
                    db.execute("UPDATE users SET username = :username, email = :email, phone = :phone, direction = :direction, pass_hash = :pass_hash, photo = :image WHERE user_id = :user_id", \
                        {"username": username, "email": email, "phone": phone, "direction": direccion, "pass_hash": password_encriptado, "image": imagen, "user_id": session["user_id"]})
                else:
                    db.execute("UPDATE users SET username = :username, email = :email, phone = :phone, direction = :direction, pass_hash = :pass_hash WHERE user_id = :user_id", \
                        {"username": username, "email": email, "phone": phone, "direction": direccion, "pass_hash": password_encriptado, "user_id": session["user_id"]})

                # Guardar cambios en la base de datos
                db.commit()

                flash("¡Los datos del usuario se actualizaron correctamente!", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")

                return redirect(url_for("configuraciones"))


            # Validar datos de entrada para el formulario de negocio
            if business_name or business_direccion or business_phone or business_descripcion or ampmStart or ampmEnd:
                if imagen2:
                    db.execute("UPDATE businesses SET business_name = :business_name, direction = :business_address, phone = :business_phone, description = :business_description, startime = :ampm_start, endtime = :ampm_end, photo = :image WHERE business_id = :business_id", \
                        {"business_name": business_name, "business_address": business_direccion, "business_phone": business_phone, "business_description": business_descripcion, "ampm_start": ampmStart, "ampm_end": ampmEnd, "image": imagen2, "business_id": session["business_id"]})
                else:
                    db.execute("UPDATE businesses SET business_name = :business_name, direction = :business_address, phone = :business_phone, description = :business_description, startime = :ampm_start, endtime = :ampm_end WHERE business_id = :business_id", \
                        {"business_name": business_name, "business_address": business_direccion, "business_phone": business_phone, "business_description": business_descripcion, "ampm_start": ampmStart, "ampm_end": ampmEnd, "business_id": session["business_id"]})

                db.commit()

                flash("¡Los datos del negocio se actualizaron correctamente!", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")

                return redirect(url_for("configuraciones"))

        else:
            return render_template("login.html")

        return redirect(url_for("configuraciones"))


@app.route("/cart", methods=["GET", "POST"])
def cart():
    if request.method == "GET":
        if "user_id" in session:
            dataOrders = db.execute("SELECT * FROM orders WHERE user_id = :user_id AND status = '1' ORDER BY business_id",\
                 {"user_id": session["user_id"]}).fetchall()
            
            ListaResponse = []

            for i in dataOrders:
                dataDetails = db.execute("SELECT * FROM orders_details WHERE order_id = :order_id", {"order_id": i['order_id']}).fetchall()
                
                temporal = {
                    "Business": db.execute("SELECT * FROM businesses WHERE business_id = :business_id", {"business_id": i["business_id"]}).fetchone()['business_name'],
                    "total": i.total,
                    "status": i.status,
                    "date_created": i.date_created,
                    "pago": i.pago,
                    "detalles": dataDetails
                }
                
                ListaResponse.append(temporal)

            context = {
                "dataResponse": ListaResponse,
            }

            return render_template("basket.html", context=context)
        else:
            return render_template("login.html")
        
    elif request.method == "POST":
        # TODO
        product_id = request.form.get("product_id")
        cantProduct = request.form.get("cantProduct")
        business_id = request.form.get("business_id")

        print(f"\n\Business ID: {business_id}\n\n")

        # Consulta a la tabla productos para obtener el precio del producto
        dataProduct = db.execute("SELECT * FROM products WHERE product_id = :product_id", {"product_id": product_id}).fetchone()
        business_id = dataProduct.business_id

        dataOrder = db.execute("SELECT * FROM orders WHERE user_id = :user_id AND status = '1' AND business_id = :business_id", {"user_id": session["user_id"], "business_id": business_id}).fetchone()
        
        priceTotal = dataProduct['unit_price'] * int(cantProduct)

        if dataOrder is None:
            db.execute("INSERT INTO orders (user_id, business_id, total, status, date_created, pago) VALUES (:user_id, :business_id, :total, '1', :date_created, :pago)", \
                {"user_id": session["user_id"], "business_id": business_id, "total": 0, "date_created": datetime.now(), "pago": 0})
            db.commit()

            dataOrder = db.execute("SELECT * FROM orders WHERE user_id = :user_id AND status = '1' AND business_id = :business_id", {"user_id": session["user_id"], "business_id": business_id}).fetchone()

        print(f"\n\nORDER: {dataOrder}\n\n")

        # Crear el items para mi tabla orders_details
        db.execute("INSERT INTO orders_details (order_id, product_id, product_name, price_unit, quantity, pricetotal) \
            VALUES (:order_id, :product_id, :product_name, :price_unit, :quantity, :pricetotal)", \
            {"order_id": dataOrder["order_id"], "product_id": product_id, "product_name": dataProduct['product_name'], "price_unit": dataProduct['unit_price'], "quantity": cantProduct, "pricetotal": priceTotal})
        
        db.commit()

        dataDetails = db.execute("SELECT * FROM orders_details WHERE order_id = :order_id", {"order_id": dataOrder["order_id"]}).fetchall()
        
        print(f"\n\nDATOS DE ORDENES: {dataDetails[0]}\n\n")

        total = db.execute("SELECT SUM(pricetotal) FROM orders_details WHERE order_id = :order_id", {"order_id": dataOrder["order_id"]}).fetchone()
        print(f"\n\nTOTAL: {total[0]}\n\n")
        
        db.execute("UPDATE orders SET total = :total WHERE order_id = :order_id", {"total": total[0], "order_id": dataOrder["order_id"]})
        db.commit()

        return "Agregado al carrito"


# Route confirmar compra
@app.route("/confirmar", methods=["GET", "POST"])
def confirmar():
    if request.method == "GET":
        if "user_id" in session:
            dataOrders = db.execute("SELECT * FROM orders WHERE user_id = :user_id AND status = '1'", {"user_id": session["user_id"]}).fetchone()

            # Verifico si el usuario tiene un pedido en proceso
            if dataOrders:
                db.execute("UPDATE orders SET status = '2' WHERE order_id = :order_id", {"order_id": dataOrders["order_id"]})
                db.commit()

                flash("Compra realizada con éxito", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")
                return redirect(url_for("cart"))   

            return redirect(url_for("cart"))
        else:
            return redirect(url_for("login"))
    elif request.method == "POST":
        return redirect(url_for("cart"))


@app.route("/historial", methods=["GET", "POST"])
def historial():
    if request.method == "GET":
        if "user_id" in session:
            dataOrders = db.execute("SELECT * FROM orders WHERE user_id = :user_id AND status = '2'", {"user_id": session["user_id"]}).fetchall()

            # verificar si el usuario tiene algun pedido en proceso
            if dataOrders:
                dataDetails = db.execute("SELECT * FROM orders_details WHERE order_id = :order_id", {"order_id": dataOrders[0]["order_id"]}).fetchall()
                
            if dataOrders and dataDetails:
                context = {
                    "dataOrders": dataOrders,
                    "dataDetails": dataDetails,
                }
                

                return render_template("history.html", context=context)
            else:
                flash("No tienes ningún pedido realizado", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")
                return redirect(url_for("cart"))
        else:
            return redirect(url_for("login"))
            
    elif request.method == "POST":
        return redirect(url_for("cart"))


@app.route("/recuperar_contrasena", methods=["GET", "POST"])
def recoverPassword():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("inicio"))
        else:
            return render_template("recover_password.html")
    
    elif request.method == "POST":
        getEmail = request.form.get("email")
        print(f"\n\nEMAIL GET {getEmail}\n\n")
        dataUser = db.execute("SELECT * FROM users WHERE email = :email", {"email": getEmail}).fetchone()
        
        if dataUser is None:
            flash("El email ingresado no existe en la base de datos", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
            return render_template("recover_password.html")

        username = dataUser["username"]
        email = dataUser["email"]

        print("\n\nUsername: {} and Correo: {}\n\n".format(username, email))

        msg = Message("Restauración de contraseña", sender="Administración", recipients=[email])        
        msg.body = f"Ha recibido este correo electrónico porque ha solicitado restablecer la contraseña para su cuenta en Services Delivery\n\n\
Por favor, vaya a la página siguiente y escoja una nueva contraseña. http://127.0.0.1:5000/update_password\n\n\
Su nombre de usuario en caso de que lo haya olvidado: {username}\n\n\
¡Gracias por usar nuestro sitio!\n\n\n\n\
Att: El equipo de Services Delivery."
        
        mail.send(msg)

        return render_template("done.html")


@app.route("/consultas_clientes", methods=["GET", "POST"])
def query_client():
    if request.method == "GET":
        return redirect(url_for("questions"))
    
    elif request.method == "POST":
        # TODO
        # Obtener datos del formulario
        nameClient = request.form.get("nameClient")
        emailClient = request.form.get("emailClient")
        messageClient = request.form.get("messageClient")
        
        # Verifico que los campos no esten vacios
        if nameClient == "" or emailClient == "" or messageClient == "":
            flash("No puede dejar campos vacios", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
            return render_template("query_client.html")

        msg = Message(nameClient, sender="{}".format(emailClient), recipients=['victorherrera1316@gmail.com'])
        msg.body = f"Ha recibido un mensaje del cliente {nameClient}\n\n\
El mensaje es: {messageClient}\n\n\
Att: {nameClient}."
        
        mail.send(msg)
        
        return redirect(url_for("questions"))


# Route para mostrar las questions frecuentes
@app.route("/preguntas_frecuentes")
def questions():
    return render_template("questions.html")


# Route update password
@app.route("/update_password", methods=["GET", "POST"])
def updatePassword():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("inicio"))
        else:
            return render_template("update_password.html")
    
    elif request.method == "POST":
        getUsername = request.form.get("username")
        getPassword = request.form.get("password")
        getPassword2 = request.form.get("confirmation")
        getEmail = request.form.get("email")

        if not getUsername or not getPassword or not getPassword2 or not getEmail:
            flash("Por favor rellena todos los campos.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639678645/gykhoa7pa3q25fp6ax7s.png")
            # return render_template("register.html", **context)
            return redirect(url_for("updatePassword"))

        if getPassword != getPassword2:
            flash("Las contraseñas no coinciden.", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639678645/gykhoa7pa3q25fp6ax7s.png")
            return redirect(url_for("updatePassword"))

        if db.execute("SELECT * FROM users WHERE email = :email AND username = :username", {"email": getEmail, "username": getUsername}).rowcount != 0:
            
            password_encriptado_update = generate_password_hash(getPassword)

            db.execute("UPDATE users SET pass_hash = :password WHERE email = :email", {"password": password_encriptado_update, "email": getEmail})

            db.commit()

            # Redireccionar a la pagina de inicio
            flash("¡La contraseña se actualizo correctamente!", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679081/qp8uyrtrl9ojuf4cfccf.png")
            return redirect(url_for("login"))

        else:
            flash("El usuario no existe en la base de datos", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
            return redirect(url_for("updatePassword"))


# Route para search de business
@app.route("/busqueda", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("inicio"))
        else:
            return redirect(url_for("login"))
    
    elif request.method == "POST":
        getSearch = request.form.get("search")

        if (not getSearch):
            # return "Ingresa datos"
            flash("Debes ingresar datos para ayudarte a búscar...", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
            return redirect(url_for("search"))
        
        if (all(i.isspace() for i in getSearch)):
            flash("Debes ingresar datos para ayudarte a búscar...", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
            return redirect(url_for("search"))

        else:
            getSearch = (f"%{getSearch}%").upper()
        
            dataBusiness = db.execute("SELECT * FROM businesses WHERE UPPER(business_name) LIKE :business_name OR UPPER(description) LIKE :description OR UPPER(direction) LIKE :direction LIMIT 10", {"business_name": getSearch, "description": getSearch, "direction": getSearch}).fetchall()
            dataCategory = db.execute("SELECT category_id, category FROM business_category").fetchall()

            # Verificar que el usuario existe
            if dataBusiness is None:
                flash("No se encontraron resultados", "https://res.cloudinary.com/cloudinary-vruiz/image/upload/v1639679685/ip80vmduijjbpir28bzt.png")
                return render_template("index.html")

            context = {
                "dataBusinessSearch": dataBusiness,
                "dataCategorySearch": dataCategory
            }

        return render_template("index.html", context=context)


@app.route("/logout")
def logout():
    # TODO
    if request.method == "GET":
        if "user_id" in session:
            session.pop("user_id")
            session.pop("username")
            session.pop("administrador")
            session.clear()

            return render_template("logout.html")
        else:
            return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)