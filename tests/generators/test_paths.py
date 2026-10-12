from pewpy.generators.paths import DATA, REPOSITORY


def test_the_tools_write_into_the_games_data_folder() -> None:
    assert DATA == REPOSITORY / "data"
    assert (DATA / "levels" / "sceneries.json").is_file()
    assert (REPOSITORY / "src" / "pewpy" / "generators" / "paths.py").is_file()
