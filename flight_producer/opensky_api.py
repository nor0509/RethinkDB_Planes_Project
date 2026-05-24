import requests


def get_flights():
    url = "https://opensky-network.org/api/states/all?lamin=49.0&lomin=14.0&lamax=55.0&lomax=24.0"

    response = requests.get(url)

    if response.status_code == 200:
        print("API request succeded")
        data = response.json()
        return data
    else:
        print(f"API request failed. Error: {response.status_code}")
        return None


def parse_flights(flights_raw):
    "Parsing the json the api responds with to the desired standard"
    flights = []
    for flight_raw in flights_raw:
        callsign = (
            flight_raw[1].strip() if isinstance(flight_raw[1], str) else "Unknown"
        )
        country = flight_raw[2].strip() if isinstance(flight_raw[2], str) else "Unknown"

        flight = {
            "id": flight_raw[0],
            "callsign": callsign,
            "origin_country": country,
            "time_position": flight_raw[3],
            "longitude": flight_raw[5],
            "latitude": flight_raw[6],
            "baro_altitude": flight_raw[7],
            "on_ground": flight_raw[8],
            "velocity": flight_raw[9],
            "true_track": flight_raw[10],
            "vertical_rate": flight_raw[11],
            "geo_altitude": flight_raw[13],
        }
        flights.append(flight)
    return flights
