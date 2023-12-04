import requests

# Define your URL
url = 'http://api.encar.com/search/car/list/general?count=false&q=(And.Hidden.N._.(C.CarType.A._.(C.Manufacturer.%ED%98%84%EB%8C%80._.ModelGroup.%EA%B7%B8%EB%9E%9C%EC%A0%80.)))&inav=%7CMetadata%7CSort'

# Define your headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en,ko;q=0.9,tr;q=0.8,ru;q=0.7',
    'Connection': 'keep-alive',
    'Host': 'api.encar.com',
    'Origin': 'http://www.encar.com',
    'Referer': 'http://www.encar.com/',
}

# Define your cookies
cookies = {
    '_encar_hostname': 'http://www.encar.com',
    'cto_bundle': '1N4SLF9qdWE1Yk5hY3dicmtjeDZqWnFxcnFjd3BpRmVJSkMlMkZsdkV0azk4ZERYYU9ZdjNSSEtLaWFoTlhJbWwwSnBLVGoyMiUyRnI0NG82SnlHd3RpMG5oVXRxMGx3VXRMJTJCTzdvTkZBczQxVFJiZ1JCU3I1c2R4M1F5RWZ0QUp3WVVXRU1WaTE5N3oyJTJGRzRlbkFMd0NoJTJGcDI4REk3Skt4M2dUaXFpZjJ4ZzZDMkVXeGhRcVUlMkJpeXEwaHlLQUh1NjdFVmcxemtiMU1BcVgxV0k3dnVnJTJGYm5yQUhTWVElM0QlM0Q',
    'AF_SYNC': '1701652523853',
    '_ga_BQ7RK9J6BZ': 'GS1.1.1701674727.5.0.1701674727.60.0.0',
    'JSESSIONID': 'VD4cbokASjVgSa7OPIVh4XHHlDwaXdqpLc8QkMs6ZdLNPeqXnvD81RO09tckTWN3.mono-was2-prod_servlet_encarWeb5',
    'WMONID': '5bPyRCUPVzy'
    # Add more cookies as needed
}

# Make the request
response = requests.get(url, headers=headers, cookies=cookies)

# Check the response
if response.status_code == 200:
    # Process the response content here
    print(response.content)
else:
    print(f"Request failed with status code {response.status_code}")
