import os
import time
from datetime import datetime

import requests

AUTH_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"


class OpenSkyClient:
    def __init__(self):
        """Initializes the OpenSky client and attempts to load API credentials from environment variables."""
        self.token = None
        self.expires_at = 0
        self.client_id, self.client_secret = self._load_credentials()

    def _load_credentials(self):
        """Retrieves OpenSky API client credentials from environment variables."""
        client_id = os.getenv("OPEN_SKY_CLIENT_ID")
        client_secret = os.getenv("OPEN_SKY_CLIENT_SECRET")
        return client_id, client_secret

    def _log(self, message):
        """Helper method to print formatted log messages with a timestamp and severity level."""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [INFO] {message}")

    def is_authenticated(self):
        """Returns True if the client has a valid, non-expired token."""
        return self.token is not None and time.time() < self.expires_at

    def _get_token(self):
        """Performs the OAuth2 client credentials flow to obtain a valid access token from OpenSky."""
        if not self.client_id or not self.client_secret:
            return None
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        try:
            response = requests.post(AUTH_URL, data=data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.expires_at = time.time() + (
                    token_data.get("expires_in", 1800) - 120
                )
                return self.token
        except requests.exceptions.RequestException as e:
            self._log(f"Auth request failed: {e}")
        return None

    def get_flights(self):
        """
        Orchestrates the flight data request, ensuring a valid token is present.
        Falls back to guest mode if authentication is unavailable.
        """
        if not self.token or time.time() >= self.expires_at:
            if not self._get_token():
                self._log("Guest mode: no credentials or auth failed")
                return self._make_request(authenticated=False)
            else:
                self._log("Authenticated successfully")
        return self._make_request(authenticated=True)

    def _make_request(self, authenticated):
        """Sends a GET request to the OpenSky API, handles authentication headers, and returns the parsed data."""
        url = "https://opensky-network.org/api/states/all?lamin=49.0&lomin=14.0&lamax=55.0&lomax=24.0"
        headers = {"Authorization": f"Bearer {self.token}"} if authenticated else {}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                self._log("API request succeeded")
                return self.parse_flights(response.json().get("states", []))
            else:
                self._log(f"API request failed with status: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            self._log(f"Network error: {e}")
            return None

    def parse_flights(self, flights_raw):
        """Transforms the raw nested list response from the API into a structured list of dictionaries."""
        flights = []
        for flight_raw in flights_raw:
            flight = {
                "id": flight_raw[0],
                "callsign": flight_raw[1].strip()
                if isinstance(flight_raw[1], str)
                else "Unknown",
                "origin_country": flight_raw[2].strip()
                if isinstance(flight_raw[2], str)
                else "Unknown",
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
