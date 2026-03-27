import json, uuid, urllib.request, urllib.error
from urllib.parse import urlencode

BASE = 'http://127.0.0.1:8000'


def req(method, path, headers=None, data=None):
    url = BASE + path
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
    r = urllib.request.Request(url, method=method, data=body)
    if headers:
        for k,v in headers.items():
            r.add_header(k,v)
    if data is not None:
        r.add_header('Content-Type','application/json')
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            return resp.getcode(), resp.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='ignore')

# register + login
email = f"smoke_{uuid.uuid4().hex[:8]}@example.com"
password = 'TestPass123!'
reg_payload = {"email": email, "password": password, "full_name": "Smoke Test"}
reg_code, reg_body = req('POST', '/api/v1/auth/register', data=reg_payload)

login_code, login_body = req('POST', '/api/v1/auth/login', data={"email": email, "password": password})
if login_code >= 400:
    # fallback OAuth form style
    form = urlencode({'username': email, 'password': password}).encode('utf-8')
    r = urllib.request.Request(BASE + '/api/v1/auth/login', method='POST', data=form)
    r.add_header('Content-Type', 'application/x-www-form-urlencoded')
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            login_code = resp.getcode()
            login_body = resp.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        login_code = e.code
        login_body = e.read().decode('utf-8', errors='ignore')

print('REGISTER', reg_code)
print('LOGIN', login_code)

token = None
user_id = None
if login_code < 400:
    try:
        lb = json.loads(login_body)
        token = lb.get('access_token')
        user_id = lb.get('user',{}).get('id')
    except Exception:
        pass

headers = {'Authorization': f'Bearer {token}'} if token else {}

spec = json.load(urllib.request.urlopen(BASE + '/openapi.json'))
paths = spec.get('paths', {})

results = []
for path, ops in paths.items():
    if path in ['/openapi.json','/docs','/redoc']:
        continue
    for method, meta in ops.items():
        m = method.upper()
        if m not in ['GET','POST','PUT','PATCH','DELETE']:
            continue
        p = path
        # substitute path params
        while '{' in p and '}' in p:
            a = p.index('{'); b = p.index('}', a)
            name = p[a+1:b]
            val = str(uuid.uuid4())
            if name == 'user_id' and user_id:
                val = user_id
            elif name.endswith('_id') and 'assessment' in name:
                val = str(uuid.uuid4())
            p = p[:a] + val + p[b+1:]

        payload = None
        if m in ['POST','PUT','PATCH']:
            payload = {}

        h = dict(headers)
        code, body = req(m, p, headers=h, data=payload)
        results.append((m, path, code))

server_errors = [r for r in results if r[2] >= 500]
okish = [r for r in results if r[2] < 500]
print('TOTAL_CALLS', len(results))
print('NON_5XX', len(okish))
print('SERVER_ERRORS', len(server_errors))
for m,p,c in server_errors[:50]:
    print('5XX', c, m, p)
