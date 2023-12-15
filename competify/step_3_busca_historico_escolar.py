import logging
import os

import pandas as pd
import pymysql as pincel
from jinja2 import Environment, FileSystemLoader

from helpers import desired_student_ids, existing_student_ids
from step import Step


logger = logging.getLogger(__name__)


class Step3(Step):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        jinja_env = Environment(loader=FileSystemLoader(self.QUERY_TEMPLATE_FOLDER))
        self.query_template = jinja_env.get_template(self.QUERY_TEMPLATE_HISTORICO_ESCOLAR)

    def __fetch_academic_results(self, student_id, connection):
        logging.info(f'Buscando dados da aluna {student_id}')

        query = self.query_template.render(student_id = student_id)
        dataframe = pd.read_sql(query, con=connection)
        if len(dataframe) > 0:
            dataframe.to_csv(f'{self.CLASS_SCORES_PATH}/{student_id}.csv', index=False)
        else:
            logging.warning(f'Aluno {student_id} não tem dados.')

    def execute(self):
        logging.info('Passo 3: busca os históricos escolares no Pincel')

        with pincel.connect(
            host=self.config['SGE']['SGE_HOSTNAME'],
            db=self.config['SGE']['SGE_DATABASE'],
            user=self.config['SGE']['SGE_USERNAME'],
            password=self.config['SGE']['SGE_PASSWORD']
            ) as connection:

            student_ids = desired_student_ids() - existing_student_ids()
            n_students = len(student_ids)

            if n_students == 0:
                logging.info('\tTodos os históricos já estão na pasta student_data/historicos. Nada novo para baixar.')

            for index, student_id in enumerate(student_ids):
                logging.info(f'{index+1} de {n_students}')
                self.__fetch_academic_results(student_id, connection)


if __name__ == '__main__':
    Step3().execute()
