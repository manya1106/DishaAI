from app.scoring.engine import calculate_percentile_ranks


def test_percentile_normalisation_ordering():
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    ranks = calculate_percentile_ranks(values, invert=False)
    assert ranks[0] == 0.0
    assert ranks[-1] == 100.0
    assert ranks == [0.0, 25.0, 50.0, 75.0, 100.0]


def test_percentile_normalisation_inversion():
    # Lower is better (e.g. competition density)
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    ranks = calculate_percentile_ranks(values, invert=True)
    assert ranks[0] == 100.0
    assert ranks[-1] == 0.0
    assert ranks == [100.0, 75.0, 50.0, 25.0, 0.0]


def test_percentile_ties_receive_average():
    values = [10.0, 20.0, 20.0, 40.0]
    ranks = calculate_percentile_ranks(values, invert=False)
    # 20.0 is tied at rank indices 2 and 3 -> avg rank = 2.5 out of 4 -> ((2.5 - 1) / 3) * 100 = 50.0
    assert ranks[1] == ranks[2]
    assert ranks[1] == 50.0
