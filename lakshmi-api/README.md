# API e interface Web do Lakshmi

![Tests](https://github.com/irpagnossin/lakshmi/actions/workflows/tests.yml/badge.svg)

Este é o microsserviço que expõe a API REST para administrar candidatos, vagas e recomendações. Os dois primeiros são CRUD, mas as recomendações só podem ser lidas (apenas [lakshmi](../lakshmi/README.md) pode criar e atualizar recomendações).

## Ambiente de desenvolvimento

1. Crie um arquivo `.env` na raiz do projeto usando como exemplo o arquivo [.env.eg](./.env.eg).
2. Execute:
```bash
docker compose up -d
```

## Ambiente de testes

**Passo 1**:
```bash
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install tox
```

**Passo 2**:
```bash
tox
```


1. Acesse a pasta `api`
1. Instale as dependências: `pip install -rrequirements.txt -rrequirements_dev.txt`.
1. Para executar os testes, execute `tox`. Para testes individuais, use o `pytest` diretamente. Por exemplo:
```bash
$ pytest tests/candidates/test_get_candidates.py -k test_requires_authentication
```

## Imagem OCI

Execute o comando abaixo para construir a imagem deste microsserviço:
```bash
docker compose build
```
Essa imagem pode, então, ser publicada num registro de imagens. Por exemplo (mais detalhes [aqui](https://cloud.google.com/container-registry/docs/pushing-and-pulling?hl=pt_br)):
```bash
docker tag lakshmi-api:0.9.0 gcr.io/irpagnossin/lakshmi-api:0.9.0
docker push gcr.io/irpagnossin/lakshmi-api:0.9.0
```

## TODO

Execute `grep -r "TODO:" *` na raiz do projeto.
