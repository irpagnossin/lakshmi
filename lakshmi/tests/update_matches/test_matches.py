import os

from tests.schemas.candidate import Candidate
from tests.schemas.position import JobPosition
from app.main import update_matches
from pymongo import MongoClient
from tests.helpers import cleanup
from datetime import datetime


db = MongoClient(os.environ["MONGODB_URL"]).get_default_database()


def common_scenario(position_id):
    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 70, '2': 50}, dirty=True)
    db.candidates.insert_one(candidate.dict())

    position = JobPosition(position_id=position_id, carreer_id=10,
                           traits={'11': [1, 2]}, weights={'11': 100},
                           dirty=True)
    db.positions.insert_one(position.dict())


@cleanup(db)
def test_created_at_is_set_and_updated_at_is_none_on_creating_match():
    position_id = 99

    common_scenario(position_id)

    # When a new match is created...
    update_matches()

    match = db.matches.find_one({'position_id': position_id})

    # ... field "created_at" is set to a timestamp...
    assert 'created_at' in match
    assert match['created_at'] is not None
    assert isinstance(match['created_at'], datetime)

    # ... and field "updated_at" is empty
    assert 'updated_at' in match
    assert match['updated_at'] is None


@cleanup(db)
def test_created_at_is_preserved_and_updated_at_is_set_on_updating_match():
    position_id = 99

    common_scenario(position_id)
    update_matches()

    match = db.matches.find_one({'position_id': position_id})
    created_at = match['created_at']

    db.positions.update_one(
        {'position_id': position_id},
        {'$set': {'dirty': True}}
    )

    # When an existing match is updated...
    update_matches()

    updated_match = db.matches.find_one({'position_id': position_id})

    # ... field "created_at" remains unchanged...
    assert updated_match['created_at'] == created_at

    # ... and field "updated_at" is set to a timestamp
    assert updated_match['updated_at'] is not None
    assert isinstance(updated_match['updated_at'], datetime)
    assert updated_match['updated_at'] > updated_match['created_at']


@cleanup(db)
def test_update_matches_when_candidate_is_dirty():
    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 70, '2': 50}, dirty=False)
    db.candidates.insert_one(candidate.dict())

    position = JobPosition(position_id=99, carreer_id=10,
                           traits={'11': [1, 2]}, weights={'11': 100})
    db.positions.insert_one(position.dict())

    update_matches()

    candidate_dirty = Candidate(candidate_id='2', carreer_id=10,
                                traits={'1': 80, '2': 50})
    db.candidates.insert_one(candidate_dirty.dict())

    update_matches()

    match = db.matches.find_one({'position_id': 99})
    recommendations = match['candidates']

    assert len(recommendations) == 2
    assert recommendations[0]['candidate_id'] == candidate_dirty.candidate_id
    assert recommendations[1]['candidate_id'] == candidate.candidate_id


@cleanup(db)
def test_update_matches_when_position_is_dirty():
    candidate_1 = Candidate(candidate_id='1', carreer_id=10,
                            traits={'1': 90, '2': 10})
    candidate_2 = Candidate(candidate_id='2', carreer_id=10,
                            traits={'1': 10, '2': 90})
    db.candidates.insert_many([candidate_1.dict(), candidate_2.dict()])

    # First, job position favors skills from category 11...
    position = JobPosition(position_id=99, carreer_id=10, traits={'11': [1],
                           '22': [2]}, weights={'11': 100, '22': 0})
    db.positions.insert_one(position.dict())

    update_matches()

    # Then, job position favors skills from category 22. As a consequence,
    # it becomes dirty...
    db.positions.update_one(
        {'position_id': position.position_id},
        {'$set': {'dirty': True, 'weights': {'11': 0, '22': 100}}}
    )

    update_matches()

    match = db.matches.find_one({'position_id': position.position_id})
    recommendations = match['candidates']

    # ... and gives precedance to candidate 2
    assert len(recommendations) == 2
    assert recommendations[0]['candidate_id'] == candidate_2.candidate_id
    assert recommendations[1]['candidate_id'] == candidate_1.candidate_id


@cleanup(db)
def test_matches_distinguish_carreers():
    candidates = [
        Candidate(candidate_id='1', carreer_id=10, traits={'1': 90}),
        Candidate(candidate_id='2', carreer_id=10, traits={'1': 80}),
        Candidate(candidate_id='3', carreer_id=20, traits={'1': 30}),
        Candidate(candidate_id='4', carreer_id=20, traits={'1': 40}),
        Candidate(candidate_id='5', carreer_id=20, traits={'1': 50})
    ]
    db.candidates.insert_many([c.dict() for c in candidates])

    positions = [
        JobPosition(position_id=99, carreer_id=10, traits={'11': [1]},
                    weights={'11': 100}),
        JobPosition(position_id=88, carreer_id=20, traits={'11': [1]},
                    weights={'11': 100}),
    ]
    db.positions.insert_many([p.dict() for p in positions])

    update_matches()

    match = db.matches.find_one({'carreer_id': positions[0].carreer_id})
    recommendations = match['candidates']
    assert len(recommendations) == 2
    assert recommendations[0]['candidate_id'] == '1'
    assert recommendations[1]['candidate_id'] == '2'

    match = db.matches.find_one({'carreer_id': positions[1].carreer_id})
    recommendations = match['candidates']
    assert len(recommendations) == 3
    assert recommendations[0]['candidate_id'] == '5'
    assert recommendations[1]['candidate_id'] == '4'
    assert recommendations[2]['candidate_id'] == '3'


@cleanup(db)
def test_candidates_with_no_required_traits_are_ignored():
    # Candidate possess trait ID 1...
    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 100})
    db.candidates.insert_one(candidate.dict())

    # ... but job position requires trait ID 2
    position = JobPosition(position_id=99, carreer_id=10, traits={'11': [2]},
                           weights={'11': 100})
    db.positions.insert_one(position.dict())

    update_matches()

    match = db.matches.find_one({'position_id': position.position_id})
    assert len(match['candidates']) == 0


@cleanup(db)
def test_positions_without_trait_requirements_are_ignored():
    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 100})
    db.candidates.insert_one(candidate.dict())

    position = JobPosition(position_id=99, carreer_id=10, traits={},
                           weights={})
    db.positions.insert_one(position.dict())

    update_matches()

    match = db.matches.find_one({'position_id': position.position_id})
    assert not match


@cleanup(db)
def test_employer_prefers_soft_skills():
    candidates = [
        Candidate(candidate_id='1', carreer_id=10,
                  traits={'1': 55,    # trait ID 1 is some hard skill
                          '2': 45}),  # trait ID 2 is some soft skill
        Candidate(candidate_id='2', carreer_id=10,
                  traits={'1': 45, '2': 55})
    ]
    db.candidates.insert_many([c.dict() for c in candidates])

    position = JobPosition(position_id=99, carreer_id=10,
                           traits={'11': [1], '22': [2]},
                           weights={'11': 40, '22': 60})

    db.positions.insert_one(position.dict())

    update_matches()

    match = db.matches.find_one({'position_id': position.position_id})
    recommendations = match['candidates']
    assert len(recommendations) == 2
    assert recommendations[0]['candidate_id'] == candidates[1].candidate_id
    assert recommendations[0]['score'] == 51
    assert recommendations[1]['candidate_id'] == candidates[0].candidate_id
    assert recommendations[1]['score'] == 49


@cleanup(db)
def test_employer_prefers_higher_skilled_candidate():
    candidates = [
        Candidate(candidate_id='1', carreer_id=10, traits={'1': 50}),
        Candidate(candidate_id='2', carreer_id=10, traits={'1': 70})
    ]
    db.candidates.insert_many([c.dict() for c in candidates])

    position = JobPosition(position_id=7, carreer_id=10, traits={'99': [1]},
                           weights={'99': 100})
    db.positions.insert_one(position.dict())

    update_matches()

    match = db.matches.find_one({'position_id': 7})
    recommendations = match['candidates']

    assert match['carreer_id'] == 10
    assert len(recommendations) == 2
    assert recommendations[0]['candidate_id'] == '2'
    assert recommendations[1]['candidate_id'] == '1'


@cleanup(db)
def test_candidates_perform_differently_for_distinct_positions():
    carreer_id = 10

    candidates = [
        Candidate(candidate_id='1', carreer_id=carreer_id,
                  traits={'1': 90, '2': 5}),
        Candidate(candidate_id='2', carreer_id=carreer_id,
                  traits={'1': 80, '2': 6}),
        Candidate(candidate_id='3', carreer_id=carreer_id,
                  traits={'1': 70, '2': 7}),
        Candidate(candidate_id='4', carreer_id=carreer_id,
                  traits={'1': 60, '2': 8}),
        Candidate(candidate_id='5', carreer_id=carreer_id,
                  traits={'1': 50, '2': 9})
    ]
    db.candidates.insert_many([c.dict() for c in candidates])

    positions = [
        JobPosition(position_id=99, carreer_id=carreer_id, traits={'11': [1]},
                    weights={'11': 100}),
        JobPosition(position_id=88, carreer_id=carreer_id, traits={'11': [2]},
                    weights={'11': 100}),
    ]
    db.positions.insert_many([p.dict() for p in positions])

    update_matches()

    match = db.matches.find_one({'position_id': positions[0].position_id})
    recommendations = match['candidates']
    assert len(recommendations) == 5
    assert recommendations[0]['candidate_id'] == candidates[0].candidate_id
    assert recommendations[1]['candidate_id'] == candidates[1].candidate_id
    assert recommendations[2]['candidate_id'] == candidates[2].candidate_id
    assert recommendations[3]['candidate_id'] == candidates[3].candidate_id
    assert recommendations[4]['candidate_id'] == candidates[4].candidate_id

    match = db.matches.find_one({'position_id': positions[1].position_id})
    recommendations = match['candidates']
    assert len(recommendations) == 5
    assert recommendations[0]['candidate_id'] == candidates[4].candidate_id
    assert recommendations[1]['candidate_id'] == candidates[3].candidate_id
    assert recommendations[2]['candidate_id'] == candidates[2].candidate_id
    assert recommendations[3]['candidate_id'] == candidates[1].candidate_id
    assert recommendations[4]['candidate_id'] == candidates[0].candidate_id
