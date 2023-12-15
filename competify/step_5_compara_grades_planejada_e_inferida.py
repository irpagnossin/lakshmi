import logging

import pandas as pd

from step import Step


logger = logging.getLogger(__name__)


class Step5(Step):
    def execute(self):
        logging.info('Passo 5: verifica se a grade inferida dos históricos é '
                     'consistente com a grade planejada')

        sqlite = self.config['SQLITE']['connection']

        grade = pd.read_sql('planned_curriculum', con=sqlite)
        disciplinas_presentes = pd.read_sql('inferred_curriculum', con=sqlite)

        juncao = grade.merge(disciplinas_presentes, on='disciplina')

        if len(grade) == len(juncao):
            logging.info('\tOK: as grades são consistentes')
        else:
            logging.warning('\tNOK: as grades NÃO são consistentes. '
                            'Os próximos passos podem não ser confiáveis')


if __name__ == '__main__':
    Step5().execute()
