from test.test_builders import build_app_environment
from unittest import TestCase

import responses

from matchpredictor.app import create_app


class TestUpcomingGamesApi(TestCase):

    @responses.activate
    def setUp(self) -> None:
        super().setUp()

        responses.add(
            method="GET",
            url="https://example.com/some.csv",
            status=200,
            body="""season,date,league_id,league,team1,team2,spi1,spi2,prob1,prob2,probtie,proj_score1,proj_score2,importance1,importance2,score1,score2,xg1,xg2,nsxg1,nsxg2,adj_score1,adj_score2
                2021,2021-08-11,2411,Barclays Premier League,Manchester United,Chelsea,79.99,85.88,0.3664,0.3843,0.2494,1.48,1.52,53.5,61.0,4,0,2.34,1.27,1.36,1.29,3.92,0.0
                2021,2021-09-17,1818,UEFA Champions League,Chelsea,Valencia,84.04,76.67,0.5901,0.1932,0.2167,1.93,1.01,81.3,85.8,0,1,3.11,0.88,2.44,0.72,0.0,1.05""",
        )

        responses.add(
            method="GET",
            url="https://example.com/regression.csv",
            status=200,
            body="""season,date,league_id,league,team1,team2,spi1,spi2,prob1,prob2,probtie,proj_score1,proj_score2,importance1,importance2,score1,score2,xg1,xg2,nsxg1,nsxg2,adj_score1,adj_score2
2021,2022-03-16,2411,Barclays Premier League,Brighton and Hove Albion,Tottenham Hotspur,74.6,79.88,0.3044,0.4363,0.2594,1.22,1.51,0.3,41.0,0,2,1.24,1.92,1.68,1.06,0.0,2.1
2021,2022-03-16,2412,English League Championship,Luton Town,Preston North End,48.52,47.82,0.4198,0.2644,0.3158,1.14,0.84,28.8,7.6,4,0,1.89,0.77,1.16,1.37,4.2,0.0
2021,2022-03-16,2412,English League Championship,Blackpool,Sheffield United,41.91,53.86,0.2715,0.4554,0.2731,1.06,1.45,6.7,34.2,0,0,0.81,0.36,1.03,1.47,0.0,0.0
2021,2022-03-16,2412,English League Championship,Nottingham Forest,Queens Park Rangers,49.28,45.02,0.4514,0.2609,0.2877,1.34,0.95,32.2,26.8,3,1,2.5,1.26,1.49,0.54,2.73,1.05
2021,2022-03-16,2412,English League Championship,Peterborough United,Swansea City,23.93,41.21,0.2351,0.4889,0.276,0.92,1.45,8.5,0.4,2,3,1.18,2.93,1.47,2.13,2.1,3.15
2021,2022-03-16,2412,English League Championship,Millwall,Huddersfield Town,43.52,44.36,0.3715,0.3144,0.3141,1.08,0.97,18.2,34.1,2,0,2.1,0.69,1.22,0.93,2.1,0.0
2021,2022-03-16,2412,English League Championship,Coventry City,Hull City,49.56,36.8,0.5499,0.1805,0.2695,1.52,0.74,21.4,2.6,0,2,1.92,0.64,2.75,0.88,0.0,2.1
2021,2022-03-16,2412,English League Championship,Cardiff City,Stoke City,43.27,45.62,0.3745,0.3268,0.2987,1.17,1.07,0.0,1.8,2,1,1.36,0.76,0.81,0.61,2.1,1.05
2021,2022-03-16,1818,UEFA Champions League,Juventus,Villarreal,74.31,81.48,0.3124,0.4231,0.2645,1.13,1.36,20.8,56.1,0,3,1.47,2.39,1.29,0.88,0.0,3.15
2021,2022-03-16,1818,UEFA Champions League,Lille,Chelsea,69.92,89.3,0.1203,0.6232,0.2565,0.48,1.48,29.1,100.0,1,2,1.37,1.1,0.85,0.51,1.05,2.1
2021,2022-03-16,2411,Barclays Premier League,Arsenal,Liverpool,82.18,92.83,0.2211,0.5531,0.2258,1.15,1.93,62.8,93.6,0,2,0.57,1.24,0.51,0.81,0.0,2.1
2022,2022-03-16,2160,United Soccer League,Atlanta United 2,New York Red Bulls II,10.31,5.82,0.5478,0.2092,0.243,1.73,0.97,16.6,8.6,0,1,0.13,2.8,0.17,2.61,0.0,0.84
2021,2022-03-17,1820,UEFA Europa League,Red Star Belgrade,Rangers,55.16,64.06,0.3184,0.4105,0.271,1.2,1.4,19.4,41.9,2,1,2.31,0.86,1.5,0.79,2.1,1.05
2021,2022-03-17,10281,UEFA Europa Conference League,Stade Rennes,Leicester City,73.41,69.84,0.4783,0.279,0.2427,1.75,1.29,100.0,100.0,2,1,1.73,0.69,1.9,1.05,2.1,1.05
2021,2022-03-17,1820,UEFA Europa League,Bayer Leverkusen,Atalanta,77.67,77.9,0.4428,0.3234,0.2338,1.83,1.54,100.0,100.0,0,1,1.56,0.72,1.35,1.17,0.0,1.05
2021,2022-03-17,10281,UEFA Europa Conference League,Basel,Marseille,53.06,66.82,0.2558,0.5037,0.2405,1.21,1.79,46.5,100.0,1,2,0.54,2.0,0.58,1.55,1.05,2.1
2021,2022-03-17,10281,UEFA Europa Conference League,AZ,Bodo/Glimt,66.85,57.69,0.5611,0.2008,0.2381,1.81,0.98,100.0,73.6,2,2,2.06,0.89,1.85,0.97,2.1,2.1
2021,2022-03-17,10281,UEFA Europa Conference League,FC Copenhagen,PSV,61.64,73.7,0.3267,0.4407,0.2327,1.56,1.84,100.0,100.0,0,4,0.35,2.13,1.03,1.51,0.0,4.2
2021,2022-03-17,1820,UEFA Europa League,Galatasaray,Barcelona,45.54,84.94,0.0503,0.8107,0.139,0.46,2.47,6.5,100.0,1,2,0.46,3.2,0.9,2.65,1.05,2.1
2021,2022-03-17,1820,UEFA Europa League,AS Monaco,Braga,71.87,65.03,0.559,0.1655,0.2755,1.46,0.66,100.0,45.2,1,1,1.05,0.53,1.88,0.74,1.05,1.05
2021,2022-03-17,2411,Barclays Premier League,Everton,Newcastle,63.77,66.73,0.4364,0.2919,0.2717,1.41,1.1,59.9,8.4,1,0,0.82,0.84,0.84,1.54,1.05,0.0
2021,2022-03-17,10281,UEFA Europa Conference League,Feyenoord,FK Partizan Belgrade,72.95,50.3,0.6995,0.1064,0.194,2.11,0.68,100.0,48.4,3,1,1.67,0.43,1.19,0.51,3.15,1.05
2021,2022-03-17,1820,UEFA Europa League,Lyon,FC Porto,72.11,79.29,0.347,0.3979,0.2551,1.4,1.52,100.0,100.0,1,1,1.25,0.65,0.78,1.65,1.05,1.05
2021,2022-03-17,10281,UEFA Europa Conference League,LASK Linz,Slavia Prague,53.28,64.48,0.2837,0.4603,0.256,1.2,1.6,58.1,100.0,4,3,1.53,0.86,1.67,0.63,3.57,3.15
2021,2022-03-17,10281,UEFA Europa Conference League,KAA Gent,PAOK Salonika,56.81,53.64,0.4886,0.1986,0.3128,1.22,0.66,67.3,42.1,1,2,1.43,0.94,1.92,0.88,1.05,2.1
2021,2022-03-17,10281,UEFA Europa Conference League,AS Roma,Vitesse,72.65,54.55,0.6534,0.1379,0.2087,2.04,0.81,100.0,72.6,1,1,1.49,0.47,1.1,0.59,1.05,1.05
2021,2022-03-17,1820,UEFA Europa League,Eintracht Frankfurt,Real Betis,69.48,72.49,0.3989,0.3515,0.2496,1.57,1.46,84.6,100.0,1,1,1.2,1.3,1.01,2.03,1.05,1.05
2021,2022-03-17,1820,UEFA Europa League,West Ham United,Sevilla FC,74.3,75.67,0.4305,0.2719,0.2976,1.25,0.93,100.0,100.0,2,0,2.78,0.95,2.45,0.89,2.1,0.0""",
        )

        app_environment = build_app_environment(football_data_api_key="my-api-key")
        app = create_app(app_environment)
        app.config["TESTING"] = True
        self.test_client = app.test_client()

    @responses.activate
    def test_list(self) -> None:
        sample_football_data_response = """{
            "matches": [
                {
                    "area": {
                        "name": "Netherlands",
                        "code": "NLD"
                    },
                    "competition": {
                        "name": "Eredivisie",
                        "code": "DED",
                        "type": "LEAGUE"
                    },
                    "homeTeam": {
                        "name": "FC Groningen",
                        "shortName": "Groningen",
                        "tla": "GRO"
                    },
                    "awayTeam": {
                        "name": "AFC Ajax",
                        "shortName": "Ajax",
                        "tla": "AJA"
                    }
                },
                {
                    "area": {
                        "name": "England",
                        "code": "ENG"
                    },
                    "competition": {
                        "name": "Championship",
                        "code": "ELC",
                        "type": "LEAGUE"
                    },
                    "homeTeam": {
                        "name": "Luton Town FC",
                        "shortName": "Luton Town",
                        "tla": "LUT"
                    },
                    "awayTeam": {
                        "name": "Sunderland AFC",
                        "shortName": "Sunderland",
                        "tla": "SUN"
                    }
                }
            ]
        }
        """

        responses.add(
            method="GET",
            url="https://api.football-data.org/v4/matches?dateFrom=2023-06-01&dateTo=2023-06-10",
            status=200,
            body=sample_football_data_response,
        )

        response = self.test_client.get("/upcoming-games/2023-06-01")

        expected_body = {
            "games": [
                {
                    "league": "Dutch Eredivisie",
                    "home": "Groningen",
                    "away": "Ajax",
                },
                {
                    "league": "English League Championship",
                    "home": "Luton Town",
                    "away": "Sunderland",
                },
            ]
        }

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_body, response.get_json())

        self.assertEqual(1, len(responses.calls))

        recorded_request = responses.calls[0].request
        self.assertEqual("my-api-key", recorded_request.headers["X-Auth-Token"])

    @responses.activate
    def test_list__with_no_mapping_for_the_league(self) -> None:
        sample_football_data_response = """{
                    "matches": [
                        {
                            "area": {
                                "name": "MiddleEarth",
                                "code": "MID"
                            },
                            "competition": {
                                "name": "BattleForTheRing",
                                "code": "BFR",
                                "type": "LEAGUE"
                            },
                            "homeTeam": {
                                "name": "Gondor",
                                "shortName": "Gondor",
                                "tla": "GON"
                            },
                            "awayTeam": {
                                "name": "The Shire FC",
                                "shortName": "The Shire",
                                "tla": "TSH"
                            }
                        }
                    ]
                }
                """

        responses.add(
            method="GET",
            url="https://api.football-data.org/v4/matches?dateFrom=2023-06-01&dateTo=2023-06-10",
            status=200,
            body=sample_football_data_response,
        )

        response = self.test_client.get("/upcoming-games/2023-06-01")

        expected_body = {
            "games": [
                {
                    "league": "MiddleEarth BattleForTheRing",
                    "home": "Gondor",
                    "away": "The Shire",
                }
            ]
        }

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_body, response.get_json())

    def test_list__when_date_is_invalid(self) -> None:
        response = self.test_client.get("/upcoming-games/this-is-not-a-date")
        self.assertEqual(400, response.status_code)

    @responses.activate
    def test_list__with_unexpected_json_from_football_data(self) -> None:

        responses.add(
            method="GET",
            url="https://api.football-data.org/v4/matches?dateFrom=2023-06-01&dateTo=2023-06-10",
            status=200,
            body='{"hello":"world"}',
        )

        response = self.test_client.get("/upcoming-games/2023-06-01")

        self.assertEqual(503, response.status_code)

    @responses.activate
    def test_list__with_invalid_json(self) -> None:

        responses.add(
            method="GET",
            url="https://api.football-data.org/v4/matches?dateFrom=2023-06-01&dateTo=2023-06-10",
            status=200,
            body="this is not json",
        )

        response = self.test_client.get("/upcoming-games/2023-06-01")

        self.assertEqual(503, response.status_code)
