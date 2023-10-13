
import os
from flask import Flask, abort, redirect, render_template, request, send_file, session, url_for
from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, storage, firestore, auth
from datetime import datetime, timedelta
import os
import urllib3
from werkzeug.utils import secure_filename

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
        usuario_data = session.get('usuario_data', None)
        # Obter todas as músicas da coleção 'musicas'
        tracks_ref = db.collection('musicas')
        tracks = tracks_ref.stream()

        # Criar uma lista para armazenar os dados das faixas
        tracks_data = []

       
        # Iterar sobre as faixas e adicionar os dados à lista
        for track in tracks:
            track_data = track.to_dict()
            track_data['id'] = track.id  # Adicionar o ID do documento à lista
            tracks_data.append(track_data)
            print(tracks_data)

        if usuario_data:
            # Exibir dados do usuário
            
            return render_template("index.html",tracks_data = tracks_data,  user = usuario_data)
        else:
                # Se a sessão não contiver dados do usuário, redirecionar para a página de login
                
            return render_template("index.html",tracks_data = tracks_data, user="")

@app.route('/sucesso_upload')
def suc():
    msg = "Projecto enviado com sucesso! volte a pagina inicial"
    return render_template("success.html", msg = msg)


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



@app.route('/uploaddd', methods=['POST'])
def uploadd():
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
        posicao = request.form['posicao']

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
            'posicao':posicao,
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



@app.route('/publicar_musica')
def pub_musica():
    # Recuperar dados do usuário da sessão
    usuario_data = session.get('usuario_data', None)

    if usuario_data:
        # Exibir dados do usuário
        return render_template("post.html", user = usuario_data)
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


@app.route('/details-page/<track_id>')
def details_page(track_id):
    # Tentar recuperar a track do Firestore usando o ID fornecido
    track_ref = db.collection('musicas').document(track_id)
    track_snapshot = track_ref.get()

    # Verificar se a track existe
    if not track_snapshot.exists:
        abort(404)  # Ou redirecione para uma página de erro 404

    # Extrair dados da track
    track_data = track_snapshot.to_dict()

    # Recuperar dados do usuário da sessão
    usuario_data = session.get('usuario_data', None)

    # Obter todas as músicas da coleção 'musicas'
    tracks_ref = db.collection('musicas')
    tracks = tracks_ref.stream()

    # Criar uma lista para armazenar os dados das faixas relacionadas
    tracks_data_related = []

    # Iterar sobre as faixas e adicionar os dados à lista
    for track in tracks:
        track_dataa = track.to_dict()
        track_dataa['id'] = track.id  # Adicionar o ID do documento à lista

        # Excluir a faixa principal da lista de faixas relacionadas
        if track.id != track_id:
            tracks_data_related.append(track_dataa)

    if usuario_data:
        # Exibir dados do usuário
        return render_template('detail-page.html', related=tracks_data_related, track=track_data, user=usuario_data)
    else:
        return render_template('detail-page.html', related=tracks_data_related, track=track_data, user=None)




@app.route('/upload', methods=['POST'])
def upload():
    # Obter dados do formulário
    titulo = request.form['titulo']
    album = request.form['album']
    message = request.form['message']

    # Recuperar dados do usuário da sessão
    usuario_data = session.get('usuario_data', None)

    # Verificar se foram fornecidos arquivos
    if 'ficheiro' not in request.files or 'capa' not in request.files:
        return redirect(request.url)

    ficheiro = request.files['ficheiro']
    capa = request.files['capa']

    # Verificar se os nomes de arquivo são válidos
    if ficheiro.filename == '' or capa.filename == '':
        return redirect(request.url)

    # Adicionar carimbo de data e hora aos nomes de arquivo
    agora = datetime.now().strftime("%Y%m%d%H%M%S")
    ficheiro_nome = secure_filename(f'tracks/{agora}_{ficheiro.filename}')
    capa_nome = secure_filename(f'covers/{agora}_c{capa.filename}')

    # Enviar arquivos para o Firebase Storage com o tipo de conteúdo especificado
    ficheiro_blob = bucket.blob(ficheiro_nome)
    capa_blob = bucket.blob(capa_nome)

    ficheiro_blob.upload_from_file(ficheiro, content_type=ficheiro.content_type)
    capa_blob.upload_from_file(capa, content_type=capa.content_type)

    # Definir a validade dos URLs (por exemplo, 10 anos)
    validade_infinita = timedelta(days=365 * 10)

    # Gerar URLs de download com validade "infinita"
    ficheiro_url = ficheiro_blob.generate_signed_url(expiration=validade_infinita, method="GET")
    capa_url = capa_blob.generate_signed_url(expiration=validade_infinita, method="GET")

    # Adicionar dados ao Firestore
    doc_ref = db.collection('musicas').add({
        'titulo': titulo,
        'album': album,
        'message': message,
        'ficheiro_url': ficheiro_url,
        'capa_url': capa_url,
        'timestamp': datetime.now(),
        'usuario_id': usuario_data.get('uid', ''),  # Assumindo que 'uid' é a chave correta
        'nome_completo': usuario_data.get('nome_completo', ''),
        'nome_artistico': usuario_data.get('nome_artistico', ''),
        'foto_perfil_url': usuario_data.get('foto_perfil', ''),
    })

    return render_template("success.html", msg=f"Seu projeto foi publicado com sucesso {usuario_data.get('nome_completo', '')}")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")



if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 5000))
    app.run(debug=True)