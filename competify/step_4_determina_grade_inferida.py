import glob
import logging

import pandas as pd

from helpers import normalize_string
from step import Step


logger = logging.getLogger(__name__)


class Step4(Step):
    def execute(self):
        """Disciplinas presentes nos históricos escolares

        Lê os históricos escolares dos alunos analisados e, a partir deles,
        identifica todas as disciplinas PRESENTES nesses históricos, de modo
        que possamos compará-las com as disciplinas que compõem a grade
        e com o mapeamento disciplina-competências.
        """
        logging.info('Passo 4: infere a grade a partir dos históricos escolares')

        todas_disciplinas = [
            self.__disciplinas(file_name)
            for file_name in glob.glob(self.CLASS_SCORES_MASK)
        ]

        pd.concat(todas_disciplinas) \
            .drop_duplicates() \
            .sort_values() \
            .to_sql(
                'inferred_curriculum',
                con=self.config['SQLITE']['connection'],
                if_exists='replace',
                index=False
            )

    def __disciplinas(self, file_name):
        return pd.read_csv(file_name).disciplina.drop_duplicates().apply(normalize_string)


if __name__ == '__main__':
    Step4().execute()
