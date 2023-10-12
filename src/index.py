
import os
from flask import Flask, redirect, render_template, request, url_for
from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, storage, firestore, auth
from datetime import datetime


app = Flask(__name__)

# Configurar credenciais do Firebase
cred = credentials.Certificate("pub-music.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'crymoney-16fd9.appspot.com'})

# Configurar o cliente de armazenamento
bucket = storage.bucket()

# Configurar o cliente do Firestore
db = firestore.client()


@app.route('/')
def home():
   
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def portfolio():
    
    return render_template("contact.html")


@app.route('/listing-page')
def contact():
    return render_template("listing-page.html")


@app.route('/postar')
def postar():
    return render_template("upload.html")

@app.route('/conta')
def conta():
    return render_template("login.html")



@app.route('/upload', methods=['POST'])
def upload():
    if 'file' in request.files:
        file = request.files['file']
        blob = bucket.blob(file.filename)
        blob.upload_from_string(file.read(), content_type=file.content_type)

        # Salve metadados no Firestore
        file_data = {
            'name': file.filename,
            'url': blob.public_url,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        db.collection('files').add(file_data)

    return redirect(url_for('home'))



# Rota para a página de cadastro
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        nome_artistico = request.form['nome_artistico']
        email = request.form['email']
        telefone = request.form['telefone']
        password = request.form['password']

        # Adicione a data de cadastro
        data_cadastro = datetime.now()

        # Adicione o usuário ao Firestore
        usuario_data = {
            'nome_completo': nome_completo,
            'nome_artistico': nome_artistico,
            'email': email,
            'telefone': telefone,
            'data_cadastro': data_cadastro,
            'foto_perfil': 'default.png'
        }

        db.collection('usuarios').add(usuario_data)

        return redirect(url_for('sucesso_cadastro'))

    return render_template('cadastro.html')

# Rota para a página de sucesso de cadastro
@app.route('/sucesso_cadastro')
def sucesso_cadastro():
    return "Cadastro realizado com sucesso!"



# Rota para a página de login
@app.route('/auth_login', methods=['POST'])
def auth_login():
    email = request.form['email']
    password = request.form['password']

    try:
        # Autenticar o usuário
        user = auth.sign_in_with_email_and_password(email, password)

        # Pode adicionar mais lógica aqui se necessário

        return redirect(url_for('sucesso_login'))

    except auth.AuthError as e:
        # Tratar erros de autenticação, se necessário
        print(f"Erro de autenticação: {e}")
        return "Falha na autenticação"

# Rota para a página de sucesso de login
@app.route('/sucesso_login')
def sucesso_login():
    return "Login bem-sucedido!"



@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")



if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 5000))
    print(os.getcwd())
    app.run(debug=True)