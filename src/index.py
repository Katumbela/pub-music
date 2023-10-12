
import os
from flask import Flask, redirect, render_template, request, session, url_for
from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, storage, firestore, auth
from datetime import datetime


app = Flask(__name__)

app.secret_key = '2023_pub-music_katumbela'  # Substitua com uma chave secreta segura

# Configurar credenciais do Firebase
cred = credentials.Certificate("pub-music.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'crymoney-16fd9.appspot.com'})

# Configurar o cliente de armazenamento
bucket = storage.bucket()

# Configurar o cliente do Firestore
db = firestore.client()


# Função para atualizar a sessão antes de cada solicitação
@app.before_request
def atualizar_sessao():
    # Verificar se o usuário está autenticado
    if 'usuario_data' in session:
        # Recuperar o ID do usuário
        uid = session['usuario_data'].get('uid')

        # Atualizar os dados da sessão a partir do Firestore
        if uid:
            usuario_ref = db.collection('usuarios').document(uid)
            usuario_atualizado = usuario_ref.get().to_dict()

            # Atualizar a sessão
            session['usuario_data'].update(usuario_atualizado)

# Rota para o logout
@app.route('/sair')
def logout():
    # Limpar os dados da sessão
    session.pop('usuario_data', None)
    return redirect(url_for('home'))  # Redirecionar para a página inicial ou outra página desejada após o logout


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

        # Verificar se já existe uma conta com o mesmo e-mail ou telefone
        conta_existente = db.collection('usuarios').where('email', '==', email).get() or \
                          db.collection('usuarios').where('telefone', '==', telefone).get()

        if conta_existente:
            msg = "Já existe uma conta com esses dados. Por favor, use informações diferentes."
            return render_template('success.html', msg=msg)
        # Adicione a data de cadastro
        data_cadastro = datetime.now()

        # Adicione o usuário ao Firestore
        usuario_data = {
            'nome_completo': nome_completo,
            'nome_artistico': nome_artistico,
            'email': email,
            'telefone': telefone,
            'password':password,
            'data_cadastro': data_cadastro,
            'foto_perfil': 'https://firebasestorage.googleapis.com/v0/b/crymoney-16fd9.appspot.com/o/default.png?alt=media&token=30b3a4b7-0286-4c19-bee0-4ac6a7f5dcc2&_gl=1*1gaoxf5*_ga*MzI0NzYxNDQwLjE2OTQ0NDI3ODY.*_ga_CW55HF8NVT*MTY5NzEzOTg5MC4xNC4xLjE2OTcxNDQ5OTcuNS4wLjA.'
        }

        db.collection('usuarios').add(usuario_data)

        return redirect(url_for('sucesso_cadastro'))

    return render_template('cadastro.html')


# Rota para a página de sucesso de cadastro
@app.route('/sucesso_cadastro')
def sucesso_cadastro():
    msg = "Sua conta foi criada com sucesso, agora vamos colocar seus projectos On"
    return render_template("success.html", msg=msg)



# Rota para a página de login
@app.route('/auth_login', methods=['POST'])
def auth_login():
    email = request.form['email']
    password = request.form['password']

    # Verificar se as credenciais estão corretas no Firestore
    usuarios_ref = db.collection('usuarios')
        
    # Pelo seguinte trecho corrigido
    query = usuarios_ref.where('email', '==', email).where('password', '==', password).limit(1)
    resultados = query.stream()

    # Converta os resultados em uma lista
    resultados_lista = list(resultados)

    # Verifique se há pelo menos um documento
    if len(resultados_lista) == 1:
        # Credenciais corretas, recuperar dados do usuário e armazenar na sessão
        usuario_data = resultados_lista[0].to_dict()
        session['usuario_data'] = usuario_data

        return redirect(url_for('dashboard'))
    else:
        # Credenciais incorretas
        return "Falha na autenticação"


# Rota para a página de sucesso de login
@app.route('/sucesso_login')
def sucesso_login():
    # Recuperar dados do usuário da sessão
    usuario_data = session.get('usuario_data', None)

    if usuario_data:
        # Exibir dados do usuário
        return f"Login bem-sucedido. Dados do usuário: {usuario_data}"
    else:
        # Se a sessão não contiver dados do usuário, redirecionar para a página de login
        return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    # Recuperar dados do usuário da sessão
    usuario_data = session.get('usuario_data', None)

    if usuario_data:
        # Exibir dados do usuário
        return render_template("dashboard.html", user = usuario_data)
    else:
        # Se a sessão não contiver dados do usuário, redirecionar para a página de login
        return redirect(url_for('conta'))


@app.route('/detail-page')
def details():
    # Recuperar dados do usuário da sessão
    usuario_data = session.get('usuario_data', None)
    return render_template("detail-page.html", user = usuario_data)
    


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")



if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 5000))
    print(os.getcwd())
    app.run(debug=True)