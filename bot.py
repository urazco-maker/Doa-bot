import os
import requests
import yfinance as yf

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "8662141509"

# 🚀 SMALL-CAP HEAVY UNIVERSE (~500 yaklaşımı)
WATCHLIST = [
    # Mega cap (market anchor)
    "AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","AMD","NFLX","AVGO",

    # Growth / mid cap core
    "PLTR","SOFI","RIVN","LCID","HOOD","UPST","SNAP","SHOP","SQ","PYPL","COIN",
    "DDOG","ZS","NET","OKTA","CRWD","TEAM","MDB","SNOW","RBLX","U","TWLO",
    "AFRM","DKNG","ROKU","PINS","LYFT","UBER","W","DASH","Z","ETSY","FVRR",

    # AI / High volatility small-mid cap
    "AI","BBAI","C3AI","IONQ","SYM","SOUN","ASTS","NVTS","PLUG","ENVX","RKLB",
    "SMCI","MSTR","TEM","GCT","HIMS","OPFI","SOFI","UPST",

    # EV / energy / speculative small cap
    "NIO","XPEV","LI","QS","NKLA","WKHS","FSR","RIDE","CHPT","BLNK","GOEV",
    "FFIE","CANO","LEV","GOCO","HYLN",

    # Meme / retail / hype microcaps
    "GME","AMC","BB","KOSS","SAVA","TLRY","BYND","FUBO","WISH","CLOV","SPCE",
    "MMAT","ATER","ATER","EXPR","REV","BBBYQ",

    # Biotech (small cap heavy)
    "MRNA","BNTX","NVAX","VRTX","REGN","SRPT","IONS","EDIT","BLUE","IMRX",
    "SRNE","ACAD","AMRN","CTXR","OCGN","ITRM","CLVS","GRTX",

    # Crypto / high beta small caps
    "MARA","RIOT","COIN","HUT","BTBT","BITF","CAN","ARBK",

    # Micro cap tech / AI hype
    "SOUN","AI","BBAI","SYM","VERI","DATS","CXAI","AISP","GRRR","AIRE",

    # ETFs (market direction filter)
    "SPY","QQQ","IWM","VTI","ARKK","TQQQ"
]


def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def analyze(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="30m", progress=False)

        if data is None or len(data) < 25:
            return None

        close = float(data["Close"].iloc[-1])
        prev = float(data["Close"].iloc[-6])

        momentum = ((close - prev) / prev) * 100

        vol_avg = float(data["Volume"].mean())
        vol_now = float(data["Volume"].iloc[-1])
        vol_ratio = vol_now / vol_avg if vol_avg > 0 else 0

        high = float(data["High"].max())
        low = float(data["Low"].min())
        volatility = ((high - low) / low) * 100

        score = 0

        # 🚀 MOMENTUM ENGINE (aggressive)
        if momentum > 1.5: score += 2
        if momentum > 3: score += 3
        if momentum > 6: score += 2
        if momentum < -3: score -= 3

        # 📊 VOLUME BREAKOUT (small cap odak)
        if vol_ratio > 3: score += 5
        elif vol_ratio > 2: score += 4
        elif vol_ratio > 1.5: score += 2
        elif vol_ratio < 0.5: score -= 2

        # ⚡ VOLATILITY (small cap doğası)
        if volatility > 15: score += 3
        elif volatility > 10: score += 2

        # 🚫 RISK FILTER
        if abs(momentum) > 15: score -= 3

        return symbol, momentum, vol_ratio, volatility, score

    except:
        return None


signals = []

for s in WATCHLIST:
    r = analyze(s)

    if r:
        sym, m, v, vol, sc = r

        if sc >= 9:
            signals.append(
                f"🔥 STRONG SMALL-CAP BUY\n{sym}\nScore: {sc}/10\nMom: {m:.2f}%\nVol: {v:.2f}x\nVolatility: {vol:.2f}%"
            )

        elif sc >= 6:
            signals.append(f"👀 SMALL-CAP SETUP {sym} | Score {sc}/10")

if signals:
    send("\n\n".join(signals))
else:
    send("📊 No strong small-cap breakouts found")

print("500+ SMALL CAP SCANNER DONE")
