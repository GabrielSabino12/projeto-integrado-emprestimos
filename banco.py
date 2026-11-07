"""Camada de acesso ao banco de dados (SQLite) - Sistema de Emprestimo de Equipamentos."""
import sqlite3

ARQUIVO_BANCO = "emprestimos.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS atendente (
    id_atendente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT NOT NULL,
    login        TEXT NOT NULL UNIQUE,
    senha        TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT NOT NULL,
    matricula  TEXT NOT NULL UNIQUE,
    tipo       TEXT NOT NULL CHECK (tipo IN ('Aluno','Professor','Funcionario')),
    telefone   TEXT
);
CREATE TABLE IF NOT EXISTS equipamento (
    id_equipamento INTEGER PRIMARY KEY AUTOINCREMENT,
    nome           TEXT NOT NULL,
    patrimonio     TEXT NOT NULL UNIQUE,
    categoria      TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'Disponivel'
                   CHECK (status IN ('Disponivel','Emprestado'))
);
CREATE TABLE IF NOT EXISTS emprestimo (
    id_emprestimo    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario       INTEGER NOT NULL REFERENCES usuario(id_usuario),
    id_equipamento   INTEGER NOT NULL REFERENCES equipamento(id_equipamento),
    id_atendente     INTEGER NOT NULL REFERENCES atendente(id_atendente),
    data_emprestimo  TEXT NOT NULL,
    data_prevista    TEXT NOT NULL,
    data_devolucao   TEXT
);
"""


def conectar(arquivo=None):
    con = sqlite3.connect(arquivo or ARQUIVO_BANCO)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def criar_banco(arquivo=None):
    con = conectar(arquivo)
    con.executescript(SCHEMA)
    # atendente padrao para o primeiro acesso
    con.execute("INSERT OR IGNORE INTO atendente (nome, login, senha) VALUES (?,?,?)",
                ("Atendente do Laboratorio", "admin", "admin123"))
    con.commit()
    con.close()
