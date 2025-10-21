
# Description
1. saham-alert.py  -> RECOMMENDED, cara generic utk buy / sell saham menggunakan args
2. saham-buy-alert.py -> jika mau buy saja
3. saham-sell-alert.py -> jika mau sell saja
4. saham.py -> source awal utk test alert seperti sell

```
docker build -t saham-alert .

docker run -d --name saham-sell saham-alert --mode sell --price 620.00 --telegram-token 7677796645:AAEYLZhLLB7lhXFf2Jq7WVdSWi64FxRy4Y4 --chat-id 133717472

docker run -d --name saham-buy saham-alert --mode buy --price 600.00 --telegram-token 7677796645:AAEYLZhLLB7lhXFf2Jq7WVdSWi64FxRy4Y4 --chat-id 133717472
  
  
```

Cara pakai via CLI:
$ py -m venv venv
$ venv\Scripts\activate  # Aktifkan env (di Windows)
(venv) C:\git\python\saham>pip install yfinance pandas requests
(venv) C:\git\python\saham>python saham-alert.py --mode buy --price 620.00 --telegram-token 7677796645:AAEYLZhLLB7lhXFf2Jq7WVdSWi64FxRy4Y4 --chat-id 133717472

