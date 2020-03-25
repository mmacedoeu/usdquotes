# usdquotes

This will get currency quotes from BACEN and among them will display the lowest quote in USD

## Features

* Asynchronous I/O based on [AsyncIo](https://docs.python.org/3/library/asyncio.html)
* Async http [client](https://github.com/aio-libs/aiohttp/)
* Halo [Spinners](https://github.com/manrajgrover/halo/)
* [Typer](https://typer.tiangolo.com/) CLI
* Multi-producer single-consumer 
* Http client requests with [Scatter-Gather](http://www.enterpriseintegrationpatterns.com/patterns/messaging/BroadcastAggregate.html) Pattern

## Setup 

Install Python 3.8.2 with Pyenv:
`pyenv install 3.8.2`
Create a virtualenv:
`pyenv virtualenv 3.8.2 usdquotes`
Setup virtualenv on project folder:
`pyenv local usdquotes`
Install dependencies:
`pip install -r requeriments.txt`


## Run

Get help:

`python -m usdquotes.main --help`

```
Usage: main.py [OPTIONS] [%Y%m%d]

  USD Quotes, Get lowest currency against USD

  Provide a Date in format YYYYMMDD as argument to CLI

  Example: python -m usdquote.main 20191131

Options:
  --version             Show version info
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

```

Get version:

`python -m usdquotes.main --help`

```
Awesome USD Quotes Version: 1.0.0
```

Get Quote for specific date:

`python -m usdquotes.main 20171101`

[![asciicast](https://asciinema.org/a/tN489snunnXfi9f8217fx2f6H.svg)](https://asciinema.org/a/tN489snunnXfi9f8217fx2f6H)

## Testing

Run pytest:

`pytest`