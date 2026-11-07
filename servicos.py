"""Regras de negocio do sistema (funcionalidades RF01 a RF08)."""
from datetime import date, datetime, timedelta
import sqlite3
from banco import conectar


class ErroNegocio(Exception):
    """Erro de regra de negocio (mensagem exibida ao atendente)."""


# ---------- RF08: login ----------
def autenticar(login, senha, arquivo=None):
    con = conectar(arquivo)
    linha = con.execute(
        "SELECT * FROM atendente WHERE login = ? AND senha = ?", (login, senha)).fetchone()
    con.close()
    if linha is None:
        raise ErroNegocio("Login ou senha invalidos.")
    return dict(linha)


# ---------- RF01: cadastrar equipamento (funcionalidade 1) ----------
def cadastrar_equipamento(nome, patrimonio, categoria, arquivo=None):
    nome, patrimonio, categoria = (nome or "").strip(), (patrimonio or "").strip(), (categoria or "").strip()
    if not nome:
        raise ErroNegocio("O nome do equipamento e obrigatorio.")
    if not patrimonio:
        raise ErroNegocio("O numero de patrimonio e obrigatorio.")
    if not categoria:
        raise ErroNegocio("A categoria e obrigatoria.")
    con = conectar(arquivo)
    try:
        cur = con.execute(
            "INSERT INTO equipamento (nome, patrimonio, categoria) VALUES (?,?,?)",
            (nome, patrimonio, categoria))
        con.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ErroNegocio("Ja existe um equipamento com este numero de patrimonio.")
    finally:
        con.close()


# ---------- RF02: cadastrar usuario ----------
def cadastrar_usuario(nome, matricula, tipo, telefone="", arquivo=None):
    nome, matricula = (nome or "").strip(), (matricula or "").strip()
    if not nome or not matricula:
        raise ErroNegocio("Nome e matricula sao obrigatorios.")
    if tipo not in ("Aluno", "Professor", "Funcionario"):
        raise ErroNegocio("Tipo de usuario invalido.")
    con = conectar(arquivo)
    try:
        cur = con.execute(
            "INSERT INTO usuario (nome, matricula, tipo, telefone) VALUES (?,?,?,?)",
            (nome, matricula, tipo, telefone))
        con.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ErroNegocio("Ja existe um usuario com esta matricula.")
    finally:
        con.close()


# ---------- RF03: registrar emprestimo (funcionalidade 2) ----------
def registrar_emprestimo(id_usuario, id_equipamento, id_atendente, dias=3, arquivo=None):
    con = conectar(arquivo)
    try:
        usuario = con.execute("SELECT * FROM usuario WHERE id_usuario = ?", (id_usuario,)).fetchone()
        if usuario is None:
            raise ErroNegocio("Usuario nao encontrado.")
        equip = con.execute("SELECT * FROM equipamento WHERE id_equipamento = ?", (id_equipamento,)).fetchone()
        if equip is None:
            raise ErroNegocio("Equipamento nao encontrado.")
        if equip["status"] != "Disponivel":
            raise ErroNegocio("Equipamento ja esta emprestado.")
        hoje = date.today()
        prevista = hoje + timedelta(days=int(dias))
        cur = con.execute(
            "INSERT INTO emprestimo (id_usuario, id_equipamento, id_atendente, data_emprestimo, data_prevista) "
            "VALUES (?,?,?,?,?)",
            (id_usuario, id_equipamento, id_atendente, hoje.isoformat(), prevista.isoformat()))
        con.execute("UPDATE equipamento SET status = 'Emprestado' WHERE id_equipamento = ?", (id_equipamento,))
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


# ---------- RF04: registrar devolucao ----------
def registrar_devolucao(id_emprestimo, arquivo=None):
    con = conectar(arquivo)
    try:
        emp = con.execute("SELECT * FROM emprestimo WHERE id_emprestimo = ?", (id_emprestimo,)).fetchone()
        if emp is None:
            raise ErroNegocio("Emprestimo nao encontrado.")
        if emp["data_devolucao"] is not None:
            raise ErroNegocio("Este emprestimo ja foi devolvido.")
        con.execute("UPDATE emprestimo SET data_devolucao = ? WHERE id_emprestimo = ?",
                    (date.today().isoformat(), id_emprestimo))
        con.execute("UPDATE equipamento SET status = 'Disponivel' WHERE id_equipamento = ?",
                    (emp["id_equipamento"],))
        con.commit()
    finally:
        con.close()


# ---------- Consultas (RF05, RF06, RF07) ----------
def listar_equipamentos(somente_disponiveis=False, arquivo=None):
    con = conectar(arquivo)
    sql = "SELECT * FROM equipamento"
    if somente_disponiveis:
        sql += " WHERE status = 'Disponivel'"
    linhas = [dict(l) for l in con.execute(sql + " ORDER BY nome")]
    con.close()
    return linhas


def listar_usuarios(arquivo=None):
    con = conectar(arquivo)
    linhas = [dict(l) for l in con.execute("SELECT * FROM usuario ORDER BY nome")]
    con.close()
    return linhas


def listar_emprestimos_abertos(arquivo=None):
    con = conectar(arquivo)
    linhas = [dict(l) for l in con.execute(
        "SELECT e.id_emprestimo, u.nome AS usuario, q.nome AS equipamento, q.patrimonio, "
        "e.data_emprestimo, e.data_prevista FROM emprestimo e "
        "JOIN usuario u ON u.id_usuario = e.id_usuario "
        "JOIN equipamento q ON q.id_equipamento = e.id_equipamento "
        "WHERE e.data_devolucao IS NULL ORDER BY e.data_prevista")]
    con.close()
    return linhas


def relatorio_emprestimos(data_inicio, data_fim, arquivo=None):
    try:
        datetime.strptime(data_inicio, "%Y-%m-%d")
        datetime.strptime(data_fim, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ErroNegocio("Datas invalidas. Use o formato AAAA-MM-DD.")
    if data_inicio > data_fim:
        raise ErroNegocio("A data inicial nao pode ser maior que a data final.")
    con = conectar(arquivo)
    linhas = [dict(l) for l in con.execute(
        "SELECT e.id_emprestimo, u.nome AS usuario, q.nome AS equipamento, "
        "e.data_emprestimo, e.data_prevista, e.data_devolucao FROM emprestimo e "
        "JOIN usuario u ON u.id_usuario = e.id_usuario "
        "JOIN equipamento q ON q.id_equipamento = e.id_equipamento "
        "WHERE e.data_emprestimo BETWEEN ? AND ? ORDER BY e.data_emprestimo, e.id_emprestimo",
        (data_inicio, data_fim))]
    con.close()
    return linhas
