import logging
from argparse import ArgumentParser

from step_1_normaliza_disciplina_competencias import Step1
from step_2_determina_grade_planejada import Step2
from step_3_busca_historico_escolar import Step3
from step_4_determina_grade_inferida import Step4
from step_5_compara_grades_planejada_e_inferida import Step5
from step_6_calcula_competencias import Step6
from step_7_cadastra_candidatos import Step7


logging.basicConfig(filename='./poc.log', filemode='a', datefmt='%H:%M:%S',
                    format='%(name)s %(levelname)s %(message)s',
                    level=logging.INFO)


def main():
    STEPS = {
        1: Step1(),
        2: Step2(),
        3: Step3(),
        4: Step4(),
        5: Step5(),
        6: Step6(),
        7: Step7(),
    }

    parser = ArgumentParser(prog='poc')
    parser.add_argument('--steps', dest='steps', type=int, nargs='+',
                        help='O passo do processamento a ser executado.')

    args = parser.parse_args()

    steps = args.steps if args.steps else STEPS.keys()

    for step in sorted(steps):
        STEPS[step].execute()


if __name__ == '__main__':
    main()
