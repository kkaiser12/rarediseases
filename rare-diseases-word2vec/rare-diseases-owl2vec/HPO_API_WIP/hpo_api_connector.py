import os
from re import S, template
import pandas as pd
import requests
import pathlib
import yaml
import math
import json
import urllib
from typing import Dict, List, Tuple, Any


class HPOApiConnector(object):

    """
    Class to interact with HPO REST API (https://hpo.jax.org/webjars/swagger-ui/3.20.9/index.html?url=/api/hpo/)
    It doesn't require authorization
    """

    def __init__(self, api_config_path: str) -> None:

        """
        Initialize the interactor

        :param api_config_path: relative path of the YAML config file of the API connection
        """

        self.base_dir = pathlib.Path(__file__).absolute().parent

        config_file = str(pathlib.Path(f"{self.base_dir}/{api_config_path}").resolve())

        with open(config_file) as f:
            self.api_config = yaml.load(f, Loader=yaml.FullLoader)

        self.base_url = self.api_config["base_url"]
        self.api_headers = self.api_config["headers"]
        self.endpoints = self.api_config["endpoints"]

    def get_request(
        self, request_url: str, parameters: Dict[str, Any] = None,
    ) -> pd.DataFrame:
        """
        HPO API get request method, it accepts a list of params as stated by the API documentation.
        :param request_url: url of the API endpoint request
        :param parameters: dict with parameters to pass to the API call
        :return: Dataframe with the requested data
        """

        data = requests.get(
            url=request_url, params=parameters, headers=self.api_headers
        )
        data = data.json()
        return pd.json_normalize(data)

    def get_term_detail(
        self, request_url: str, term: str, parameters: Dict[str, Any] = None
    ) -> pd.DataFrame:
        """
        Get the details of a given term (the nested json is not being parsed)
         - name
         - id
         - definition
         - synonyms
         - xrefs
         - relations

        :param request_url: url of the API endpoint request
        :param parameters: dict with parameters to pass to the API call
        :return: pd.Dataframe with the requested data

        """

        request_url = request_url.format(hpo_term=term)
        data = self.get_request(request_url, parameters)
        return data

    def get_term_diseases(self, terms: Any) -> pd.DataFrame:
        """
        Get the possible diseases for a given term / set of terms (the nested json is not being parsed)

        :param terms: term (str) or list of terms (List[str])
        :return: pd.Dataframe with the requested data

        """

        if isinstance(terms, str):
            model_url = self.endpoints.get["term_diseases"]["model_url"]
            request_url = self.base_url + model_url.format(hpo_term=terms)
            parameters = self.endpoints.get["term_diseases"]
        elif isinstance(terms, List[str]):
            pass
        else:
            raise TypeError("The term should be a string or a list of terms")

        data = self.get_request(request_url, parameters)
        return data

    def get_endpoint_data(self, endpoint: str) -> pd.DataFrame:
        """
        Get the HPO API data from an specific endpoint.

        :param endpoint: name of the endpoint (based on the config YAML file)
        :return: pd.Dataframe with the requested data
        """

        if not self.endpoints.get(endpoint):
            raise ValueError(
                "At least one configuration object must be provided for the endpoint"
            )

        api_config_dict = self.endpoints.get(endpoint, {})

        model_url = api_config_dict["model_url"]
        request_url = self.base_url + model_url
        parameters = api_config_dict["parameters"]

        data = self.get_request(request_url, parameters)
        return data


if __name__ == "__main__":
    conn = HPOApiConnector("config/hpo.yaml")
