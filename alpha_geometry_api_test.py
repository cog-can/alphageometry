import requests

if __name__ == '__main__':
    ag_api_host = "http://127.0.0.1:8005/"
    resp = requests.get(url = ag_api_host + "get_random_txt")
    data = resp.json()

    payload = data
    resp = requests.post(url=ag_api_host + "get_graph", json=payload)
    data = resp.json()

    print(data)
