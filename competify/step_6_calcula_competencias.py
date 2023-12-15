import logging

import pandas as pd

from helpers import existing_student_ids, normalize_string
from step import Step


logger = logging.getLogger(__name__)


class Step6(Step):
    def __checa_disciplinas_duplicadas(self, student_id, dataframe):
        logging.info('\t6.1: trata disciplinas duplicadas')

        notas_deduplicadas = dataframe.groupby(by=['cpf', 'disciplina']).max('nota_final').reset_index()

        if len(dataframe) > len(notas_deduplicadas):
            logging.info(f'\t\tAluno {student_id} tem mais de uma avaliação por disciplina. Vou usar a maior nota.')

        return notas_deduplicadas


    def __checa_notas_nulas(self, student_id, dataframe):
        logging.info('\t6.2: verifica se há notas nulas')

        notas_nan = dataframe.dropna(subset=['nota_final'])
        n_notas_nan = len(notas_nan)

        if n_notas_nan == 0:
            logging.warning(f'\t\tAluno {student_id} não tem notas!')
            return None
        elif len(dataframe) > n_notas_nan:
            logging.warning(f'\t\tAluno {student_id} tem notas nulas. Continuando com o que tem.')

        return notas_nan


    def __checa_competencias_nulas(self, student_id, dataframe):
        logging.info('\t6.3: verifica se há competências')

        disciplinas_competencias = pd.read_sql('classes_competences', con=self.config['SQLITE']['connection'])
        disciplinas_competencias.disciplina = disciplinas_competencias.disciplina.apply(normalize_string)

        notas_competencias = dataframe.merge(disciplinas_competencias, on='disciplina')
        n_competencias_nan = len(notas_competencias)

        if n_competencias_nan == 0:
            logging.error(f'\t\tAluno {student_id} não tem competências. Desistindo.')
            return None
        #elif n_notas_nan > n_competencias_nan:
        #    logging.warning(f'\t\tAluno {student_id} tem disciplinas sem competências associadas. Continuando com o que tem')

        return notas_competencias


    def __checa_itens_por_competencia(self, dataframe):
        logging.info('\t6.4: verifica se a quantidade de avaliações é consistente com a grade')

        sqlite = self.config['SQLITE']['connection']

        expected_counts = (
            pd.read_sql('classes_competences', con=sqlite)
                .competence_id
                .rename('count')
                .value_counts()
                .reset_index()
                .rename(columns={'index': 'competence_id'})
        )

        current_counts = (
            dataframe
                .competence_id
                .rename('count')
                .value_counts()
                .reset_index()
                .rename(columns={'index': 'competence_id'})
        )

        merged = expected_counts.merge(current_counts, on='competence_id', suffixes=('_expected', '_current'))
        merged['items_ok'] = merged.count_current <= merged.count_expected

        return merged.items_ok.all()

    def __calcula_pontuacao_por_competencia(self, dataframe):
        logging.info('\t6.5: calcula a pontuação nas competências')

        sqlite = self.config['SQLITE']['connection']

        expected_counts = (
            pd.read_sql('classes_competences', con=sqlite)
                .competence_id
                .rename('items_count')
                .value_counts()
                .reset_index()
                .rename(columns={'index': 'competence_id'})
        )

        soma = dataframe.groupby(by=['student_id', 'cpf', 'competence_id']).sum('nota_final').reset_index()

        scaling_factor = 100 / int(self.config['ASSESSMENTS']['max'])

        merged = expected_counts.merge(soma, on='competence_id')
        merged['competence_score'] = (merged.nota_final * scaling_factor / merged.items_count).round().astype('int32')

        return merged[['student_id', 'cpf', 'competence_id', 'competence_score']]


    def __competence_scores(self, student_id):
        logging.info(f'\tAluno {student_id}...')

        notas = pd.read_csv(f'{self.CLASS_SCORES_PATH}/{student_id}.csv')
        notas.disciplina = notas.disciplina.apply(normalize_string)

        notas_deduplicadas = self.__checa_disciplinas_duplicadas(student_id, notas)
        notas_nan = self.__checa_notas_nulas(student_id, notas_deduplicadas)
        if notas_nan is None:
            return

        notas_competencias = self.__checa_competencias_nulas(student_id, notas_nan)
        if notas_competencias is None:
            return
        projecao_de_interesse = notas_competencias[self.PROJECTION]

        if not self.__checa_itens_por_competencia(projecao_de_interesse):
            logging.error(f'\tAluno {student_id} tem mais itens de avaliação que o definido na grade. Vou desistir.')
            return

        return self.__calcula_pontuacao_por_competencia(projecao_de_interesse)


    def execute(self):
        logging.info('Passo 6: calcula a pontuação em cada competência')

        student_ids = list(existing_student_ids())

        dataframes = [
            self.__competence_scores(student_id)
            for student_id in student_ids
        ]

        if any([dataframe is not None for dataframe in dataframes]):
            sqlite = self.config['SQLITE']['connection']
            pd.concat(dataframes).to_sql('competence_scores', con=sqlite,
                                         if_exists='replace', index=False)


if __name__ == '__main__':
    Step6().execute()
