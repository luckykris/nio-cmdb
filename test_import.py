import requests
headers ={
    "Authorization": "Token 8e233860bb6a1d3c9753dc131b534a3f1fc8e20d"
}
a = requests.get('http://opsdb.test-istio.gome.inc/v1/server', headers=headers)
tmp = a.json()
while tmp:
    tmp = requests.get(tmp['next'], headers=headers).json()
    for x in tmp['results']:
        data = {
            "name": x['name'],
            "namespace": None,
            "cpu": x['cpu'],
            "ip": x['ip'],
            "labels": [
                {"k": "model_name", "v": x["model_name"]},
                {"k": "site_name", "v": x["site_name"]},
                {"k": "company", "v": x["company"]},
                {"k": "os_id", "v": x["os_id"]},
                {"k": "cpu", "v": x["cpu"]},
            ]
        }
        r = requests.post("http://127.0.0.1:8000/v1/mysql/", json=data)
        print(r.text)