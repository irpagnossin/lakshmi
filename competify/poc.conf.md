# Arquivo de configuração

## Seção `CLASS_COMPETENCES`
Esta seção contém informações sobre o arquivo que contém o mapeamento entre disciplinas e competências. Veja detalhes sobre o arquivo [aqui](./inputs/README.md)
- `arquivo` é o caminho para o arquivo Excel.
- `aba` é a aba da planilha.

## Seção `STUDENTS`
- `mask` indica a máscara para identificar os arquivos que contém os ID dos alunos que queremos cadastrar.

## Seção `ASSESSMENTS`
- `max` define a escala das notas presentes no histórico escolar. Por exemplo, `max = 100` indica que as notas são dadas na escala 0-100 pontos.

## Seção `LAKSHMI`
Configurações referentes ao [lakshmi-api](../lakshmi-api/README.md):
- `candidates_endpoint` é a URL do serviço.
- `carreer_id` é o ID da carreira onde queremos cadastrar os alunos.
- `AUTH_TOKEN` é o token para acessar a API Lakshmi.

## Seção `SQLITE`
As etapas do processamento são salvas num banco de dados do SQLite:
- `connection` é a URL do arquivo do banco de dados.

## Seção `SGE`
Configurações e credenciais de acesso ao Sistema de Gestão Acadêmico (SGE), usados para consultar os históricos escolares.
- `SGE_HOSTNAME`: _host_ do sistema de banco de dados.
- `SGE_DATABASE`: banco de dados.
- `SGE_USERNAME`: usuário.
- `SGE_PASSWORD`: senha.

obs.: veja [aqui](../README.md) como criar uma versão fictícia do SGE.