from core.utils import hasher


def test_hash_list():
    d = ["1", "2" "3", "4"]

    assert hasher.hash_list(d) == hasher.hash_list(d)
    d_reversed = d.copy()
    d_reversed.reverse()

    assert not hasher.hash_list(d_reversed) == hasher.hash_list(d)
    assert not hasher.hash_list(d[:-1]) == hasher.hash_list(d)
    assert not hasher.hash_list(["random"]) == hasher.hash_list(d)


def test_hash_string():
    d = "12"

    assert hasher.hash_string(d) == hasher.hash_string(d)
    d_reversed = d[::-1]

    assert not hasher.hash_string(d_reversed) == hasher.hash_string(d)
    assert not hasher.hash_string(d[:-1]) == hasher.hash_string(d)
    assert not hasher.hash_string("random") == hasher.hash_string(d)


def test_hash_file():
    pass
