
## Lakshmi _worker_

Este é o microsserviço que efetivamente calcula as recomendações.

**Passo 1**: crie o arquivo `.env` usando como exemplo o arquivo [.env.eg](./.env.eg).

**Passo 2**: instale o projeto como de praxe:
```bash
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements_dev.txt
pip install -e .
```

**Passo 3**: em seguida, e supondo que [lakshmi-mongo](../README.md) esteja em execução, execute o comando `go-lakshmi` (um _entry-point_). Note que este microsserviço não depende da [API Lakshmi](../lakshmi-api/README.md).

## Imagem OCI

Execute o comando abaixo para construir a imagem desse microsserviço:
```bash
docker compose build
```
Essa imagem pode, então, ser publicada num registro de imagens. Por exemplo (mais detalhes [aqui](https://cloud.google.com/container-registry/docs/pushing-and-pulling?hl=pt_br)):
```bash
docker tag lakshmi:0.9.0 gcr.io/irpagnossin/lakshmi:0.9.0
docker push gcr.io/irpagnossin/lakshmi:0.9.0
```

## TODO

Execute `grep -r "TODO:" *` na raiz do projeto.

## Heurística das recomendações

_Lakshmi_ emula um avaliador, que compara as características da vaga de trabalho com as dos candidatos. A diferença - crucial - é que os candidatos têm pontuações de _competências_ (supostamente bem avaliadas. Não é o objetivo deste projeto avaliar a qualidade das avaliações de competência) e as vagas também são descritas em termos das competências necessárias.

A heurística é simples: usamos as medidas de similaridade de conjuntos [Sørensen–Dice](https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient) ou [Jaccard](https://en.wikipedia.org/wiki/Jaccard_index). Inclusive, a implementação atual usando MongoDB e um _schema_ de baixo nível foi com o intuito de implementar essas métricas no [Redis](https://redis.io/), que dá suporte a operações com conjuntos.