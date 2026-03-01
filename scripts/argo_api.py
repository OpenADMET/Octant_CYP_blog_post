import json
import os

import requests


#### Get with param filters ####
def get_factory(endpoint):
    def fn(**kwargs):
        argo_base_url = os.environ.get("ARGO_BASE_URL").rstrip("/")
        api_key = os.environ.get("ARGO_API_KEY")
        url = f"{argo_base_url}/platform_app/api/{endpoint}"
        headers = {"Authorization": api_key, "Content-Type": "application/json"}

        response = requests.get(url, headers=headers, params=kwargs, timeout=120)
        response.raise_for_status()

        response_json = json.loads(response.content)
        if isinstance(response_json, list):
            res = response_json
        else:
            res = response_json["results"]
        return res

    return fn


def get_paginated_factory(endpoint):
    def fn(**kwargs):
        argo_base_url = os.environ.get("ARGO_BASE_URL").rstrip("/")
        api_key = os.environ.get("ARGO_API_KEY")
        url = f"{argo_base_url}/platform_app/api/{endpoint}"
        headers = {"Authorization": api_key, "Content-Type": "application/json"}

        response = requests.get(url, headers=headers, params=kwargs, timeout=120)
        response.raise_for_status()
        resp_json = response.json()
        data = resp_json["results"]

        # Loop through paginated response
        next_url = resp_json.get("next", None)
        while next_url is not None:
            paginated_response = requests.get(
                url=next_url, headers=headers, timeout=120
            )
            paginated_response.raise_for_status()
            paginated_data = paginated_response.json()
            # Extend the results and assign next
            data.extend(paginated_data["results"])
            next_url = paginated_data.get("next", None)
        return data

    return fn


get_experiments = get_paginated_factory("experiments")
get_analyses = get_paginated_factory("analyses")
get_chemical_library_members = get_paginated_factory("chemical_library_members")
get_chemical_samples = get_paginated_factory("chemical_samples")
get_plates = get_factory("plates")
get_chemicals = get_paginated_factory("chemicals")


#### Get by id (pk) ####
def get_by_id_factory(endpoint, suffix=None):
    def fn(pk):
        argo_base_url = os.environ.get("ARGO_BASE_URL").rstrip("/")
        api_key = os.environ.get("ARGO_API_KEY")
        url = f"{argo_base_url}/platform_app/api/{endpoint}/{pk}"
        if suffix:  # Covers both None and "" cases
            url += "/" + suffix
        headers = {"Authorization": api_key, "Content-Type": "application/json"}

        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()

        response_json = json.loads(response.content)
        return response_json

    return fn


get_experiment_by_id = get_by_id_factory("experiments")
get_analysis_by_id = get_by_id_factory("analyses")
get_plate_by_id = get_by_id_factory("plates")
get_plate_luci_analysis_info_by_id = get_by_id_factory(
    "plates", suffix="luci_analysis_info"
)
get_analysis_data_by_id = get_by_id_factory("analyses", suffix="data")
get_chemical_libraries_by_expt_id = get_by_id_factory(
    "experiments", suffix="chemical_libraries"
)


def post_factory(endpoint):
    def fn(data):
        argo_base_url = os.environ.get("ARGO_BASE_URL").rstrip("/")
        api_key = os.environ.get("ARGO_API_KEY")
        url = f"{argo_base_url}/platform_app/api/{endpoint}"
        headers = {"Authorization": api_key, "Content-Type": "application/json"}
        data = json.dumps(data)

        response = requests.post(url, headers=headers, data=data, timeout=120)
        response.raise_for_status()

        response_json = json.loads(response.content)
        return response_json

    return fn


post_plate = post_factory("plates")


def put_factory(endpoint):
    def fn(data):
        argo_base_url = os.environ.get("ARGO_BASE_URL").rstrip("/")
        api_key = os.environ.get("ARGO_API_KEY")
        url = f"{argo_base_url}/platform_app/api/{endpoint}"
        headers = {"Authorization": api_key, "Content-Type": "application/json"}
        data = json.dumps(data)

        response = requests.put(url, headers=headers, data=data, timeout=120)
        response.raise_for_status()

        response_json = json.loads(response.content)
        return response_json

    return fn


def put_by_id_factory(endpoint, suffix=None):
    def fn(pk, data):
        argo_base_url = os.environ.get("ARGO_BASE_URL").rstrip("/")
        api_key = os.environ.get("ARGO_API_KEY")
        url = f"{argo_base_url}/platform_app/api/{endpoint}/{pk}"
        if suffix:  # Covers both None and "" cases
            url += "/" + suffix
        headers = {"Authorization": api_key, "Content-Type": "application/json"}
        data = json.dumps(data)

        response = requests.put(url, headers=headers, data=data, timeout=120)
        response.raise_for_status()

        response_json = json.loads(response.content)
        return response_json

    return fn


def patch_by_id_factory(endpoint, suffix=None):
    def fn(pk, data):
        argo_base_url = os.environ.get("ARGO_BASE_URL").rstrip("/")
        api_key = os.environ.get("ARGO_API_KEY")
        url = f"{argo_base_url}/platform_app/api/{endpoint}/{pk}"
        if suffix:  # Covers both None and "" cases
            url += "/" + suffix
        headers = {"Authorization": api_key, "Content-Type": "application/json"}
        data = json.dumps(data)

        response = requests.patch(url, headers=headers, data=data, timeout=120)
        response.raise_for_status()

    return fn


patch_luci_analysis_info_by_id = patch_by_id_factory(
    "plates", suffix="luci_analysis_info"
)
