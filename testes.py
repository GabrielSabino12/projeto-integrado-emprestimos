"""Plano de testes automatizado (CT01 a CT07) - executa contra um banco temporario."""
import os, tempfile
import servicos as s
from banco import criar_banco

arq = os.path.join(tempfile.mkdtemp(), "teste.db")
criar_banco(arq)
resultados = []


def caso(id_, descricao, esperado, funcao):
    try:
        obtido = funcao()
        ok = True
    except Exception as e:  # noqa
        obtido, ok = f"EXCECAO: {e}", False
    resultados.append((id_, descricao, esperado, obtido, "PASSOU" if ok else "FALHOU"))


def recusa(fn, trecho):
    """Retorna a mensagem de erro se o sistema recusou a operacao como esperado."""
    try:
        fn()
    except s.ErroNegocio as e:
        assert trecho in str(e), str(e)
        return f"Recusado: {e}"
    raise AssertionError("o sistema deveria ter recusado a operacao")


def ct01():
    id_ = s.cadastrar_equipamento("Notebook Dell 15", "PAT-0001", "Notebook", arq)
    assert any(e["id_equipamento"] == id_ for e in s.listar_equipamentos(arquivo=arq))
    return "Equipamento salvo e listado (id %d)" % id_

def ct02():
    return recusa(lambda: s.cadastrar_equipamento("", "PAT-0002", "Notebook", arq), "obrigatorio")

def ct03():
    s.cadastrar_equipamento("Projetor Epson", "PAT-0003", "Projetor", arq)
    s.cadastrar_usuario("Maria Souza", "2024001", "Aluno", "11999990000", arq)
    id_emp = s.registrar_emprestimo(1, 2, 1, 3, arq)
    st = [e for e in s.listar_equipamentos(arquivo=arq) if e["id_equipamento"] == 2][0]["status"]
    assert st == "Emprestado"
    return "Emprestimo %d gravado; equipamento passou a '%s'" % (id_emp, st)

def ct04():
    return recusa(lambda: s.registrar_emprestimo(1, 2, 1, 3, arq), "ja esta emprestado")

def ct05():
    return recusa(lambda: s.registrar_emprestimo(999, 1, 1, 3, arq), "Usuario nao encontrado")

def ct06():
    s.registrar_devolucao(1, arq)
    st = [e for e in s.listar_equipamentos(arquivo=arq) if e["id_equipamento"] == 2][0]["status"]
    assert st == "Disponivel" and s.listar_emprestimos_abertos(arq) == []
    return "Devolucao registrada; equipamento voltou para '%s'" % st

def ct07():
    return recusa(lambda: s.cadastrar_equipamento("Outro Notebook", "PAT-0001", "Notebook", arq), "patrimonio")

def ct08():
    s.registrar_emprestimo(1, 1, 1, 3, arq)
    nomes = [e["nome"] for e in s.listar_equipamentos(True, arq)]
    assert "Notebook Dell 15" not in nomes
    return "Disponiveis agora: %s" % nomes

casos = [
 ("CT01", "Cadastro de equipamento com dados validos", "Equipamento salvo e listado", ct01),
 ("CT02", "Cadastro de equipamento sem preencher o nome", "Mensagem de erro e nada e salvo", ct02),
 ("CT03", "Emprestimo de equipamento disponivel", "Emprestimo gravado e status 'Emprestado'", ct03),
 ("CT04", "Emprestimo de equipamento ja emprestado", "Sistema impede e avisa", ct04),
 ("CT05", "Emprestimo para usuario inexistente", "Sistema impede e avisa", ct05),
 ("CT06", "Devolucao de equipamento emprestado", "Devolucao gravada e equipamento disponivel", ct06),
 ("CT07", "Cadastro com patrimonio duplicado", "Sistema impede e avisa", ct07),
 ("CT08", "Consulta de disponiveis apos emprestimo", "Equipamento emprestado nao aparece", ct08),
]
for c in casos:
    caso(*c)

if __name__ == "__main__":
    for r in resultados:
        print(f"{r[0]} | {r[1]}\n     Esperado: {r[2]}\n     Obtido  : {r[3]}\n     Resultado: {r[4]}\n")
    print("Total: %d | Passaram: %d | Falharam: %d" % (
        len(resultados), sum(r[4] == "PASSOU" for r in resultados), sum(r[4] == "FALHOU" for r in resultados)))
