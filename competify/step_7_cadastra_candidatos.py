import json
import logging
import os
import re

import pandas as pd
from requests import get, post, put

from step import Step

logger = logging.getLogger(__name__)


class Step7(Step):
    def execute(self):
        logging.info('Passo 7: cadastra/atualiza candidatos no Lakshmi')

        sqlite = self.config['SQLITE']['connection']
        competence_scores = pd.read_sql('competence_scores', con=sqlite)

        existing_cpfs = self.__existing_candidates()

        for cpf in competence_scores.cpf.drop_duplicates():
            traits = (
                competence_scores[competence_scores.cpf == cpf]
                    [self.CANDIDATE_PROJECTION]
                    .astype({'competence_id': str})
                    .set_index('competence_id')
                    .to_dict()['competence_score']
            )

            canonical_cpf = re.sub('[^0-9]', '', cpf)
            candidate = {'candidate_id': canonical_cpf,
                         'carreer_id': self.config['LAKSHMI_API']['carreer_id'],
                         'traits': traits}

            endpoint = self.config['LAKSHMI_API']['candidates_endpoint']

            if canonical_cpf in existing_cpfs:
                response = put(f'{endpoint}/{canonical_cpf}/', data=json.dumps(candidate), headers=self.__auth_header())

                if response.status_code == 201:
                    logging.info(f'\tCandidato {canonical_cpf} foi atualizado no Lakshmi ({endpoint}/)')
                else:
                    logging.error(f'\tNao consegui atualizar o candidato {canonical_cpf}: HTTP error {response.status_code}.')
                pass
            else:
                response = post(f'{endpoint}/', json=candidate, headers=self.__auth_header())

                if response.status_code == 201:
                    logging.info(f'\tCandidato {canonical_cpf} foi cadastrado no Lakshmi ({endpoint}/)')
                else:
                    logging.error(f'\tNao consegui cadastrar o candidato {canonical_cpf}: HTTP error {response.status_code}.')

    def __existing_candidates(self):
        endpoint = self.config['LAKSHMI_API']['candidates_endpoint']
        response = get(f'{endpoint}/', params={'limit': 1300}, headers=self.__auth_header())
        if response.status_code == 401:
            print('Token inválido: Lakshmi respondeu com HTTP 401')
            exit()

        return [candidate['candidate_id'] for candidate in response.json()]


    def __auth_header(self):
        auth_token = self.config['LAKSHMI_API']['AUTH_TOKEN']
        return {"Authorization": f"Bearer {auth_token}"}

if __name__ == '__main__':
    Step7().execute()
