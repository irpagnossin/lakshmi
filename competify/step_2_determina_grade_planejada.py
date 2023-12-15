import logging

import pandas as pd

from step import Step


logger = logging.getLogger(__name__)


class Step2(Step):
    def execute(self):
        logging.info('Passo 2: determina o conjunto de disciplinas que compõem a grade planejada')

        sqlite = self.config['SQLITE']['connection']

        pd.read_sql('classes_competences', con=sqlite) \
            .disciplina \
            .drop_duplicates() \
            .to_sql('planned_curriculum', con=sqlite, if_exists='replace',
                    index=False)


if __name__ == '__main__':
    Step2().execute()
