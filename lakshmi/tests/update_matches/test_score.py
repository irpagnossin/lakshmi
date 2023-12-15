from tests.schemas.candidate import Candidate
from tests.schemas.position import JobPosition
from app.main import score


def helper_score(position: JobPosition, candidate: Candidate):
    return score(position.dict(), candidate.dict())


def test_underqualified_candidate_scores_0():
    # Candidate possess trait ID 1...
    candidate = Candidate(candidate_id=1, carreer_id=10,
                          traits={'1': 100})

    # ... but job position requests trait 2
    position = JobPosition(position_id=99, carreer_id=10, traits={'11': [2]},
                           weights={'11': 100})

    assert helper_score(position, candidate) == 0


def test_overqualified_candidate_scores_100():
    # Candidate possess trait ID 1, 2 and 3 with full score...
    candidate = Candidate(candidate_id=1, carreer_id=10,
                          traits={'1': 100, '2': 100, '3': 100})

    # ... but job position requests only traits 1 and 2
    position = JobPosition(position_id=99, carreer_id=10,
                           traits={'11': [1, 2]}, weights={'11': 100})

    assert helper_score(position, candidate) == 100


def test_some_complicated_case():
    candidate = Candidate(candidate_id=1, carreer_id=10,
                          traits={'1': 31, '2': 42, '3': 53, '4': 64, '5': 75,
                                  '6': 86, '7': 97})

    position = JobPosition(position_id=99, carreer_id=10,
                           traits={'11': [1, 3, 5, 7], '22': [2, 4, 6]},
                           weights={'11': 48, '22': 67})

    expected_score = int(round((48 * (31 + 53 + 75 + 97) / 4 + 67 * (42 + 64 + 86) / 3) / (48 + 67)))  # noqa: E501
    assert helper_score(position, candidate) == expected_score


def test_score_averages_among_required_traits():
    candidate = Candidate(candidate_id=1, carreer_id=10,
                          traits={'1': 31, '2': 42, '3': 53, '4': 64, '5': 75,
                                  '6': 86, '7': 97})

    position = JobPosition(position_id=99, carreer_id=10,
                           traits={'11': [1, 5], '22': [2, 4, 6]},
                           weights={'11': 48, '22': 67})

    expected_score = int(round((48 * (31 + 75) / 2 + 67 * (42 + 64 + 86) / 3) / (48 + 67)))  # noqa: E501
    assert helper_score(position, candidate) == expected_score


def test_skilled_candidate_scores_higher():
    candidates = [
        Candidate(candidate_id=1, carreer_id=10, traits={'1': 80}),
        Candidate(candidate_id=2, carreer_id=10, traits={'1': 79})
        ]

    position = JobPosition(position_id=99, carreer_id=10, traits={'11': [1]},
                           weights={'11': 48})

    assert helper_score(position, candidates[0]) > helper_score(position,
                                                                candidates[1])


def test_candidate_with_no_skill_scores_0():
    candidate = Candidate(candidate_id=1, carreer_id=10, traits={})
    position = JobPosition(position_id=99, carreer_id=10, traits={'11': [1]},
                           weights={'11': 48})

    assert helper_score(position, candidate) == 0
