"""Interface web (Flask) do Sistema de Controle de Emprestimo de Equipamentos."""
from datetime import date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import servicos as s
from banco import criar_banco

app = Flask(__name__)
app.secret_key = "chave-secreta-do-projeto-integrado"


def login_obrigatorio(f):
    @wraps(f)
    def interna(*args, **kwargs):
        if "atendente" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return interna


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            session["atendente"] = s.autenticar(request.form["login"], request.form["senha"])
            return redirect(url_for("emprestimos"))
        except s.ErroNegocio as e:
            flash(str(e), "erro")
    return render_template("login.html")


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("login"))


@app.route("/equipamentos", methods=["GET", "POST"])
@login_obrigatorio
def equipamentos():
    if request.method == "POST":
        try:
            s.cadastrar_equipamento(request.form["nome"], request.form["patrimonio"], request.form["categoria"])
            flash("Equipamento cadastrado com sucesso!", "ok")
        except s.ErroNegocio as e:
            flash(str(e), "erro")
        return redirect(url_for("equipamentos"))
    return render_template("equipamentos.html", lista=s.listar_equipamentos())


@app.route("/usuarios", methods=["GET", "POST"])
@login_obrigatorio
def usuarios():
    if request.method == "POST":
        try:
            s.cadastrar_usuario(request.form["nome"], request.form["matricula"],
                                request.form["tipo"], request.form.get("telefone", ""))
            flash("Usuário cadastrado com sucesso!", "ok")
        except s.ErroNegocio as e:
            flash(str(e), "erro")
        return redirect(url_for("usuarios"))
    return render_template("usuarios.html", lista=s.listar_usuarios())


@app.route("/novo-emprestimo", methods=["GET", "POST"])
@login_obrigatorio
def novo_emprestimo():
    if request.method == "POST":
        try:
            s.registrar_emprestimo(int(request.form["usuario"]), int(request.form["equipamento"]),
                                   session["atendente"]["id_atendente"], int(request.form["dias"]))
            flash("Empréstimo registrado com sucesso!", "ok")
            return redirect(url_for("emprestimos"))
        except (s.ErroNegocio, ValueError) as e:
            flash(str(e) if isinstance(e, s.ErroNegocio) else "Dados invalidos.", "erro")
    return render_template("novo_emprestimo.html", usuarios=s.listar_usuarios(),
                           equipamentos=s.listar_equipamentos(somente_disponiveis=True))


@app.route("/emprestimos")
@login_obrigatorio
def emprestimos():
    return render_template("emprestimos.html", lista=s.listar_emprestimos_abertos(),
                           hoje=date.today().isoformat())


@app.route("/devolver/<int:id_emprestimo>", methods=["POST"])
@login_obrigatorio
def devolver(id_emprestimo):
    try:
        s.registrar_devolucao(id_emprestimo)
        flash("Devolução registrada com sucesso!", "ok")
    except s.ErroNegocio as e:
        flash(str(e), "erro")
    return redirect(url_for("emprestimos"))


@app.route("/relatorio")
@login_obrigatorio
def relatorio():
    ini = request.args.get("inicio", "")
    fim = request.args.get("fim", "")
    linhas = None
    if ini and fim:
        try:
            linhas = s.relatorio_emprestimos(ini, fim)
        except s.ErroNegocio as e:
            flash(str(e), "erro")
    return render_template("relatorio.html", linhas=linhas, inicio=ini, fim=fim)


if __name__ == "__main__":
    criar_banco()
    app.run(debug=False, port=5000)
