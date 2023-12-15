# Competify

Este sub-projeto auxilia na transição entre o currículo baseado em disciplinas e aquele baseado em competências: o sistema de recomendação de competências só faz sentido no contexto da Educação baseada em Competências. Porém, isso requer alterações profundas nos currículos dos cursos, e isso pode dificultar ou inviabilizar o avanço do projeto de recomendação enquanto os sistemas de apoio ao ensino-aprendizagem não provéem o apoio adequado.

Para resolver esse problema, este sub-projeto traduz as notas dos alunos (currículo baseado em disciplinas) em pontuações de competências (currículo baseado em competências), a partir do histórico escolar do aluno, e cadastra-o no [lakshmi-api](../lakshmi-api/README.md).

Porém, **atenção**: essa tradução não é perfeita e, por isso, introduz erros. Esse método deve, então, ser abandonado assim que a transição de currículos for concluída.

## Setup

1. Instale o projeto:
```bash
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
pip install .
```

2. Crie o arquivo de configuração `poc.conf` como uma cópia do arquivo de exemplo [poc.conf.eg](./poc.conf.eg) e edite-o conforme a necessidade. Veja detalhes [aqui](./poc.conf.md).

3. Coloque na pasta `inputs` o arquivo contendo o mapeamento de competências e disciplinas (a pasta já contém um arquivo de exemplo funcional). Veja detalhes [aqui](./inputs/README.md).

4. Coloque na pasta `inputs/ids` os arquivos contendo as matrículas dos alunos que queremos cadastrar no `lakshmi-api` (a pasta já contém arquivos-exemplo funcionais). Veja detalhes [aqui](./inputs/ids/README.md).

5. Execute o comando `competity` (um _entry-point_):
```bash
competity
```

Isso executará todos os passos do processamento. Você pode executar passos individualmente, enumerados de 1 a 7, assim:
```bash
competity --steps 4 5
```

- **Passo 1**: pré-processa os nomes de disciplinas e competências, normalizando-os.
- **Passo 2**: identifica o conjunto de disciplinas únicas presentes no mapeamento entre disciplinas e competências (arquivo indicado na configuração `CLASS_COMPETENCES.arquivo` em [poc.conf](./poc.conf)) e interpreta-o como o currículo _planejado_ (baseado em disciplinas).
- **Passo 3**: busca o histórico escolar de todos os alunos cujos ID estão presentes nos arquivos indicados na configuração `STUDENTS.mask` em [poc.conf](./poc.conf). Para isso o script conecta-se no banco de dados do Sistema de Gestão Acadêmica da escola usando as configurações e credenciais presentes na seção `SGE` do arquivo de configuração [poc.conf](./poc.conf). Além disso, para que esse passo funcione é imprescindíviel disponibilizar a query SQL que faz essa consulta, uma vez para cada aluno. Para isso, substitua o conteúdo do arquivo [./queries/historico_escolar.sql.jinja] com a devida query. Note que a query é disponibilizada como um template Jinja, que ela espera receber como argumento o ID do aluno (`student_id`) e deve trazer os campos indicados no arquivo-modelo.
- **Passo 4**: identifica quais são as disciplinas únicas que compõe o que chamamos de _currículo inferido_ (dos históricos).
- **Passo 5**: verifica se os currículos planejado e inferido contém as mesmas disciplinas. Se não, dizemos que os currículos são inconsistentes e, consequentemente, qualquer cálculo de pontuação de competência a partir dos históricos (passo seguinte) não é confiável.
- **Passo 6**: calcula as pontuações de competências a partir das notas e do mapeamento entre disciplinas e competências. A heurística é a seguinte: cada disciplina desenvolve uma ou mais competências, e interpretamos a nota nessa disciplina como uma contribuição para a pontuação total de cada competência. Por exemplo, considere um currículo que contenha apenas as disciplinas _biossegurança_ e _cosmetologia_. A disciplina _biossegurança_ desenvolve as competências _1_ e _2_; e a disciplina _cosmetologia_, as competências _2_ e _3_. Suponha que um aluno tenha obtido notas 7 e 8 nas disciplinas _biossegurança_ e _cosmetologia_ (escala de 0-10), respectivamente. Como a competência _1_ está presente apenas na disciplina _biossegurança_, interpretamos a pontuação da competência _1_ como sendo 70% (=7/10). Por outro lado, a competência _2_ é desenvolvida em ambas as disciplinas. Nela, o aluno obteve um total de 7 + 8 = 15 pontos, de um total de 20 que poderia ter obtido. Logo, sua pontuação nessa competência é de 15/20 = 75%.
- **Passo 7**: cadastra os alunos (como candidatos a vagas de trabalho) e suas pontuações de competências no `lakshmi-api` utilizando as configurações na seção `LAKSHMI` em [poc.conf](./poc.conf). O parâmetro `carreer_id` define qual é o ID da carreira do aluno no `lakshmi-api`. Note ainda que é necessário definir a variável de ambiente `AUTH_TOKEN`, que autentica esse script para acessar a API.

