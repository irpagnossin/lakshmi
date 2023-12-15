from abc import ABC, abstractmethod
from configparser import ConfigParser


class Step(ABC):
    CONFIG_FILE_NAME = './poc.conf'
    QUERY_TEMPLATE_FOLDER = './queries'
    QUERY_TEMPLATE_HISTORICO_ESCOLAR = 'historico_escolar.sql.jinja'
    CLASS_SCORES_PATH = './student_data/historicos'
    CLASS_SCORES_MASK = './student_data/historicos/*.csv'
    PROJECTION = ['student_id', 'cpf', 'competence_id', 'nota_final']
    CANDIDATE_PROJECTION = ['competence_id', 'competence_score']

    def __init__(self):
        self.config = ConfigParser()
        self.config.read(self.CONFIG_FILE_NAME)

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
