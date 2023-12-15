import logging

import pandas as pd

from helpers import normalize_string
from step import Step


logger = logging.getLogger(__name__)


class Step1(Step):
    def execute(self):
        logging.info('Passo 1: normaliza o nome das disciplinas')

        input_file_name = self.config['CLASS_COMPETENCES']['arquivo']
        input_sheet_name = self.config['CLASS_COMPETENCES']['aba']

        dataframe = pd.read_excel(input_file_name, sheet_name=input_sheet_name)
        dataframe.disciplina = dataframe.disciplina.apply(normalize_string)

        dataframe.to_sql(
            'classes_competences',
            con=self.config['SQLITE']['connection'],
            if_exists='replace',
            index=False
        )


if __name__ == '__main__':
    Step1.execute()
