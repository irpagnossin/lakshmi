import logging
import os
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

from pymongo import MongoClient

load_dotenv()


db = MongoClient(os.environ["MONGODB_URL"]).get_default_database()


logging.basicConfig(filemode='a', datefmt='%H:%M:%S', level=logging.INFO,
                    format='%(name)s %(levelname)s %(message)s')


def score(position: Dict, candidate: Dict) -> int:
    score: float = 0
    total_weight: int = 0
    weights = position['weights']
    traits = position['traits']

    for category_id, trait_ids in traits.items():
        posessed_values = [
            # TODO: armazenar traid_id como str para evitar cast?
            candidate['traits'].get(str(int(trait_id)), 0)
            for trait_id in trait_ids
        ]

        score += weights[category_id] * sum(posessed_values) / len(trait_ids)
        total_weight += weights[category_id]

    score /= total_weight

    return int(round(score))


def update_position_match(position):
    position_id = int(position['position_id'])

    logging.info('Reviewing recommendations for position_id '
                 f"{position_id} (_id = {position['_id']}).")

    if 'traits' not in position or not position['traits']:
        logging.warning(f"Malformed position ID {position_id}: "
                        ' missing attribute "traits" or it is empty.')
        return

    if 'weights' not in position or not position['weights']:
        logging.warning(f"Malformed position ID {position_id}: "
                        ' missing attribute "weights" or it is empty.')
        return

    if not len(position['traits']) == len(position['weights']):
        logging.warning(f"Malformed position ID {position_id}: "
                        'attributes "traits" and "weights" must have '
                        'equal length.')
        return

    def recommendation(position, candidate):
        return {
            'candidate_id': candidate['candidate_id'],
            'score': score(position, candidate)
        }

    candidates = db.candidates.find({'carreer_id': position['carreer_id']})

    recommendations = [
        recommendation(position, candidate)
        for candidate in candidates
    ]

    logging.info(f'{len(recommendations)} candidates were reviewed as a '
                 f'consequence of position_id {position_id}  '
                 f"(_id = {position['_id']}).")

    recommendations = [r for r in recommendations if r['score'] > 0]

    match = {
        'position_id': position['position_id'],
        'carreer_id': position['carreer_id'],
        'candidates': recommendations
    }

    match['candidates'].sort(reverse=True, key=lambda c: c['score'])

    existing_match = db.matches.find_one({'position_id': position_id})

    if not existing_match:
        match['created_at'] = datetime.utcnow()
        match['updated_at'] = None
    else:
        match['updated_at'] = datetime.utcnow()

    db.matches.update_one(
        {'position_id': position['position_id']},
        {'$set': match},
        upsert=True
    )


def clean(ids, collection):
    db[collection].update_many(
        {'_id': {'$in': ids}},
        {'$set': {'dirty': False}}
    )


def update_matches():
    logging.info('Updating recommendations')

    carreer_ids = set()
    candidate_ids = []
    for candidate in db.candidates.find({'dirty': True}):
        carreer_ids.add(candidate['carreer_id'])
        candidate_ids.append(candidate['_id'])

    if candidate_ids:
        logging.info(f'{len(candidate_ids)} candidates in {len(carreer_ids)} '
                     'carreer have updated traits, so that their '
                     'recomendations are outdated.')
    else:
        logging.info('There are no recomendation outdated as a consequence '
                     'of updated candidate traits.')

    positions = db.positions.find({
        '$or': [
            {'dirty': True},
            {'carreer_id': {'$in': list(carreer_ids)}}
        ]
    })

    position_ids = []
    for position in positions:
        position_id = position['_id']
        position_ids.append(position_id)
        update_position_match(position)

    logging.info(f'Recomendation for {len(position_ids)} positions were '
                 'updated.')

    clean(candidate_ids, 'candidates')
    clean(position_ids, 'positions')


def main():
    update_matches()


if __name__ == '__main__':
    main()
