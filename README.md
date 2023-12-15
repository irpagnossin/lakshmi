# Lakshmi

Este projeto implementa um sistema de recomendação de candidatos a vagas de trabalho baseando-se nas competências requeridas pela vaga e aquelas desenvolvidas pelos candidatos ao longo de um curso cujo currículo foi construído com base na aprendizagem por competências.

O projeto é composto por dois microsserviços:
- [lakshmi-api](./lakshmi-api/README.md) é a API REST que permite cadastrar e consultar candidatos e vagas; e consultar as recomendações às vagas cadastradas.
- [lakshmi](./lakshmi/README.md) é o worker que calcula as recomendações, em batch.

Há ainda um projeto auxiliar, [competify](./competify/README.md), que calcula as competências dos candidatos (ex-alunos) a partir de históricos escolares tradicionais, isto é, baseados em disciplinas e notas. Idealmente, o Sistema de Gestão Acadêmica (SGE) deve fornecer as avaliações das competências, mas quando esse não é o caso (geralmente não é), esse sub-projeto pode ajudar.

## Demonstração

**Passo 1**: crie o arquivo `lakshmi-api/.env` usando como exemplo o arquivo [lakshmi-api/.env.eg](./lakshmi-api/.env.eg).

**Passo 2**:
```bash
docker compose up
```

Isso criará três serviços em contêineres:
- `lakshmi-api` é a API e interface Web, disponível em http://localhost e já rodando em ambiente de desenvolvimento.
- `lakshmi-mongo` é o banco de dados usado por `lakshmi-api`.
- `sge` é uma instância fictícia do SGE, que fornece alguns históricos escolares. Serve apenas para demonstrar o funcionamento de [competify](./competify/README.md).

**Passo 3**: acesse a interface Web ([aqui](http://localhost)), autentique-se com o usuário `user@company.com` e senha `user`, e veja que já cadastramos uma vaga na API (entidade `positions`). Porém, não há candidatos ainda.

**Passo 4**: acesse o sub-projeto [competify](./competify/README.md), instale-o conforme orientado, e execute o comando `poc` (um _entry-point_). Isso cadastrará alguns candidatos na API (entidade `candidates`), mas ainda não temos recomendações.

**Passo 5**: acesse o microsserviço [lakshmi](./lakshmi/README.md), instale-o conforme orientado e execute o comando `go-lakshmi` (um _entry-point_). Isso criará as recomendações à vaga: entidade `matches`.

## Lakshmi?

_Lakshmi_ é a mãe divina benevolente do hinduismo; a deusa da prosperidade... Achei oportuno.
