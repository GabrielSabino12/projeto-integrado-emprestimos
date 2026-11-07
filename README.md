# Sistema de Controle de Empréstimo de Equipamentos

Projeto Integrado – Tecnologia em Análise e Desenvolvimento de Sistemas (Anhanguera).

## Requisitos
- Python 3.10 ou superior
- Flask: `pip install flask`

## Como executar
1. `python app.py` (cria o banco `emprestimos.db` automaticamente)
2. Abrir `http://127.0.0.1:5000` no navegador
3. Login: `admin` | Senha: `admin123`

## Testes automatizados
`python testes.py`

## Arquivos
- `banco.py`: criação e conexão com o banco SQLite
- `servicos.py`: regras de negócio
- `app.py`: rotas e telas
- `templates/`: páginas HTML
- `testes.py`: plano de testes automatizado
