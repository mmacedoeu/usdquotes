from datetime import datetime
from halo import Halo
import aiohttp
import asyncio
import json
import sys

req_currencies_url = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/Moedas"
)
req_quote_url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)"
headers = {"accept": "application/json;odata.metadata=minimal"}
quote_params = {
    "format": "json",
    "$select": "cotacaoVenda",
    "$filter": "tipoBoletim%20eq%20'Fechamento%20PTAX'",
}
params = {"format": "json"}


def urlbuilder(url, params):
    r = f"{url}"
    for i, kv in enumerate(params.items()):
        k, v = kv
        if i == 0:
            r = f"{r}?{k}={v}"
        else:
            r = f"{r}&{k}={v}"
    return r


async def fetch(session, url, params):
    """
        Fetch data from url
    """
    u = urlbuilder(url, params)
    async with session.get(u) as response:
        return await response.json()


async def bcb_get_currencies(session):
    """
    Get currencies avaliable for quotes from bcb

    """
    return await fetch(session, req_currencies_url, params)


async def get_currencies(session):
    spinner = Halo(text="Fetching Avaliable Currencies", spinner="dots")
    spinner.start()
    res = await bcb_get_currencies(session)
    spinner.stop()
    return res["value"]


async def bcb_get_quote(session, symbol: str, data: str):
    """
    Get currency quote from bcb

    """
    p = quote_params
    p["@moeda"] = f"'{symbol}'"
    p["@dataCotacao"] = f"'{data}'"
    return await fetch(session, req_quote_url, p)


async def get_quote(
    session, symbol: str, data: str, min_q: asyncio.Queue, dolar_q: asyncio.Queue
) -> None:
    """
    Wait for fetching quote from BACEN,
    Detect if quote is avaliable and
    if symbol is USD send to specific
    queue or else send quotes to update_min task by proper Queue
    """
    resp = await bcb_get_quote(session, symbol, data)
    objq = resp["value"]
    quote = sys.float_info.max
    if objq:
        quote = objq[0]["cotacaoVenda"]

        if symbol == "USD":
            await dolar_q.put(quote)
            await dolar_q.put(None)
        else:
            await min_q.put((symbol, quote))

async def update_min(min, q: asyncio.Queue) -> None:
    """
    Upon receiving a None terminate the task or
    update the min dict with lowest quote if it given quote
    is lower than current lowest

    """
    while True:
        msg = await q.get()
        if msg is None:
            break
        else:
            s, quote = msg
            if quote < min["quote"]:
                min["quote"] = quote
                min["symbol"] = s
            q.task_done()


def lookup_description(symbol, currencies, min):
    """
    Filter the Avaliable currencies for the provided symbol
    and update the dict min with it's description

    """
    desc = list(filter(lambda x: x["simbolo"] == symbol, currencies))
    min["nomeFormatado"] = desc[0]["nomeFormatado"]


async def process(data: datetime):
    """
    Main processor coordinator
    Setup the producer -> consumer
    Get avaliable currencies from BACEN and
    request quotes for each 
    After fetching quotes, wait for task update_min
    and output the consolidated quote if any or print X

    """
    min_q = asyncio.Queue()
    dolar_q = asyncio.Queue()
    min = {"symbol": "", "quote": sys.float_info.max}
    strdata = data.strftime("%m-%d-%Y")
    async with aiohttp.ClientSession(trust_env=True) as session:
        currencies = await get_currencies(session)
        spinner = Halo(text="Fetching Quotes", spinner="dots")
        spinner.start()
        symbols = [c["simbolo"] for c in currencies]
        quotes_tasks = []
        for q in symbols:
            quotes_task = asyncio.ensure_future(
                get_quote(session, q, strdata, min_q, dolar_q)
            )
            quotes_tasks.append(quotes_task)

        compute_task = update_min(min, min_q)
        await asyncio.gather(*quotes_tasks)
        await min_q.put(None)
        await compute_task
        if min["symbol"]:
            lookup_description(min["symbol"], currencies, min)
        spinner.stop()

    if min["symbol"]:
        dolar = await dolar_q.get()
        print(f"{min['symbol']},{min['nomeFormatado']},{min['quote']/dolar}")
    else:
        print("x")


def run(data: datetime):
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    asyncio.run(process(data))
