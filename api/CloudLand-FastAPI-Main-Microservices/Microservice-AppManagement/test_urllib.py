import urllib.request
import json

app_id = "508068a3-040a-41cd-93a5-b5527ff7b52c"

try:
    req = urllib.request.Request(f"http://localhost:6201/api/v1/constant/?application_id={app_id}")
    with urllib.request.urlopen(req) as response:
        roots = json.loads(response.read().decode())
        
        if isinstance(roots, list) and len(roots) > 0:
            root_id = roots[0].get('Id') or roots[0].get('id')
            print("ROOT ID:", root_id)
            req2 = urllib.request.Request(f"http://localhost:6201/api/v1/constant/GetConstantRecursiveByRootId/{root_id}?application_id={app_id}")
            with urllib.request.urlopen(req2) as res2:
                tree = json.loads(res2.read().decode())
                print("TREE LENGTH:", len(tree) if isinstance(tree, list) else "Not a list")
                if isinstance(tree, list) and len(tree) > 0:
                    print("TREE HEAD:", json.dumps(tree[:3], indent=2))
except Exception as e:
    print("ERROR:", e)
