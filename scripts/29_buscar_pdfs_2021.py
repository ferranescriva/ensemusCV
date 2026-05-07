import requests, time

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
found = []

for month, day in [("08","02"),("08","16"),("08","30"),("09","01"),("09","13"),("09","27")]:
    for num in range(7000, 10000, 5):
        url = f"https://dogv.gva.es/datos/2021/{month}/{day}/pdf/2021_{num}.pdf"
        try:
            r = requests.head(url, headers=headers, timeout=4)
            size = int(r.headers.get("content-length", 0))
            if r.status_code == 200 and size > 800000:
                found.append(f"{size//1024}KB {month}/{day} 2021_{num}.pdf")
                print(f"{size//1024}KB {month}/{day} 2021_{num}.pdf")
        except:
            pass
        time.sleep(0.1)

print(f"Total: {len(found)}")