# Transpetro MLOps — backend

API, scheduler e executor de treinamentos YOLO do projeto CITI-USP/Transpetro.

## Execução local

1. Copie `.env.template` para `.env` e configure o MySQL.
2. Ative o ambiente Python e instale `requirements.txt`.
3. Em um banco novo, execute `python scripts/create_db.py`. Para atualizar o esquema anterior, execute `python scripts/migrate_release_1.py`.
4. Inicie a API com `./scripts/run_server.sh`.
5. Em outro terminal, inicie o scheduler com `./scripts/run_scheduler.sh`.

A documentação interativa fica em `http://localhost:8000/docs`.

## Testes

```bash
env/bin/python -m unittest discover -s tests -v
env/bin/python -m compileall -q app scheduler trainer scripts
```

Consulte [docs/release-1.md](docs/release-1.md) para o escopo entregue e [docs/endpoints.md](docs/endpoints.md) para o contrato HTTP.
