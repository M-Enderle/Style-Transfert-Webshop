import src.sts.utils.utils as utils

def test_load_user_toml():
    return_val = utils.load_user_toml()
    assert isinstance(return_val, dict)
    assert 'database' in return_val