from matchpredictor.app import AppEnvironment


def build_app_environment(
    csv_location: str = "https://example.com/some.csv",
    regression_csv_location: str = "https://example.com/regression.csv",
    regression_csv_include: bool = True,
    season: int = 2023,
    football_data_api_key: str = "football-data-key-100",
) -> AppEnvironment:
    return AppEnvironment(
        csv_location=csv_location,
        regression_csv_location=regression_csv_location,
        regression_csv_include=regression_csv_include,
        season=season,
        football_data_api_key=football_data_api_key,
    )
