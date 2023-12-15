import glob
import os
import re
from configparser import ConfigParser

import pandas as pd
import unidecode

from step import Step


def fetch_file_names():
    config = ConfigParser()
    config.read(Step.CONFIG_FILE_NAME)

    return glob.glob(config['STUDENTS']['mask'])


def fetch_student_ids_from_file(file_name):
    df = pd.read_csv(file_name)
    return list(df.student_id.drop_duplicates().astype(str))


def desired_student_ids():
    student_ids = []
    for file_name in fetch_file_names():
        student_ids += fetch_student_ids_from_file(file_name)

    return set(student_ids)


def normalize_string(string):
    return re.sub(' +', ' ',  unidecode.unidecode(string).lower().strip())


def existing_student_ids():
    return set([
        os.path.splitext(os.path.basename(path))[0]
        for path in glob.glob(Step.CLASS_SCORES_MASK)
    ])
