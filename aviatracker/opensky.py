import json
import logging
import socket
from typing import Dict, List, Optional
import time

from requests import exceptions, get, codes

from aviatracker.config import common_conf
from aviatracker.database import FlightAirportInfo, StateVector, OpenskyFlight

logger = logging.getLogger()


class OpenskyStates(object):
    def __init__(self, username: Optional = None, password: Optional = None) -> None:
        if username is None or password is None:
            username, password = common_conf.opensky_user, common_conf.opensky_pass
        self.auth = (username, password)
        self.api_url = "https://opensky-network.org/api"

    def get_from_opensky(self, params: Dict, operation: str) -> Dict:
        try:
            r = get(
                "{}{}".format(self.api_url, operation),
                auth=self.auth,
                params=params,  # type: ignore
                timeout=15,
            )
            if r.status_code == codes.ok:
                logger.debug("Successful connection to Opensky API.")
                response = json.loads(r.text)
                return response
            else:
                logger.error(f"Could not connect to Opensky API. Status code is {r.status_code}.")

        except (OSError, exceptions.ReadTimeout, socket.timeout) as e:
            logger.error(f"Could not get states from API: {e}")

    def get_current_states(self, time_sec: int = 0, icao24: str = None) -> Optional[List[StateVector]]:
        parameters = {"time": int(time_sec), "icao24": icao24}
        operation = "/states/all"

        resp: Dict = self.get_from_opensky(parameters, operation)

        if resp is not None:
            request_time = resp["time"]
            dirty_states = resp["states"]
            states = [StateVector(*([request_time] + state)) for state in dirty_states]
            return states

    def get_callsigns_history(self) -> List[OpenskyFlight]:
        """Get flights history for an hour interval 2 days ago"""
        begin = time.time() - 172800
        end = begin + 3600
        parameters = {"begin": begin, "end": end}
        operation = "/flights/all"

        resp: Dict = self.get_from_opensky(parameters, operation)

        if resp is not None:
            flights = [OpenskyFlight(*x) for x in resp]
            return flights

    # def get_airports(self, begin: int, end: int) -> List[FlightAirportInfo]:
    #     parameters = {"begin": begin, "end": end}
    #     operation = "/flights/all"
    #     resp = self.get_from_opensky(parameters, operation)
    #
    #     flight_airports = []
    #
    #     attempts = 3
    #     if resp is None:
    #         while attempts > 0 and resp is None:
    #             logger.info("One more try")
    #             resp = self.get_from_opensky(parameters, operation)
    #             attempts -= 1
    #
    #     for flight in resp:
    #         icao24 = flight["icao24"]
    #         dept_airport = flight["estDepartureAirport"]
    #         arrv_airport = flight["estArrivalAirport"]
    #         est_arr_time = flight["lastSeen"]
    #         flight_airports.append(FlightAirportInfo(*[icao24, dept_airport, arrv_airport, est_arr_time]))
    #
    #     return flight_airports
