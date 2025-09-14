from pathlib import Path
import toml, requests

config = {
    "api": {
        "url": "https://api.porkbun.com/api/json/v3",
        "api_key": "",
        "secret_key": "",
    },
    "domain": {
        "base_domain": "example.com",
        "ddns_subdomain": "ddns",
    },
}

def init():
    global config

    path = Path("./configuration")
    path.mkdir(parents=True, exist_ok=True)

    file = path.joinpath("config.toml")

    if file.exists():
        toml_string = file.read_text()
    else:
        toml_string = toml.dumps(config)

    config.update(toml.loads(toml_string))
    file.write_text(toml.dumps(config))

def get_ip() -> str:
    body = {
        "apikey": config["api"]["api_key"],
        "secretapikey": config["api"]["secret_key"],
    }
    url = config["api"]["url"] + "/ping"

    response = requests.post(url, json=body)

    if response.status_code == 200:
        return response.json()["yourIp"]
    else:
        return ""

def get_record_id() -> str:
    body = {
        "apikey": config["api"]["api_key"],
        "secretapikey": config["api"]["secret_key"],
    }
    url = config["api"]["url"] + "/dns/retrieve/" + config["domain"]["base_domain"]

    response = requests.post(url, json=body)
    for record in response.json()["records"]:
        if record["name"] == config["domain"]["ddns_subdomain"] + "." + config["domain"]["base_domain"]:
            return str(record["id"])

    body = {
        "apikey": config["api"]["api_key"],
        "secretapikey": config["api"]["secret_key"],
        "name": config["domain"]["ddns_subdomain"],
        "type": "A",
        "content": "1.1.1.1",
    }
    url = config["api"]["url"] + "/dns/create/" + config["domain"]["base_domain"]

    response = requests.post(url, json=body)
    return str(response.json()["id"])

def update_record(record_id: str, ip: str) -> bool:
    body = {
        "apikey": config["api"]["api_key"],
        "secretapikey": config["api"]["secret_key"],
        "name": config["domain"]["ddns_subdomain"],
        "type": "A",
        "content": ip,
    }
    url = config["api"]["url"] + "/dns/edit/" + config["domain"]["base_domain"] + "/" + record_id

    response = requests.post(url, json=body)
    return response.status_code == 200

if __name__ == "__main__":
    init()

    my_ip = get_ip()

    if my_ip == "":
        print("check your credentials")
        exit(1)

    record_id = get_record_id()

    if not update_record(record_id, my_ip):
        print("failed")
        exit(2)

    print("domain record updated")
    exit(0)
