Title: Dev Info
Date: 2017-4-6
slug: dev
toc: yes

# Locate the `TownCrier` Contract

- Network:  [Ropsten (Revived)] Testnet, instructions for syncing to the revived testnet chain can be found [here])
- Address: `0xC3847C4dE90B83CB3F6B1e004c9E6345e0b9fc27`

# Get the [attestation](https://software.intel.com/en-us/articles/intel-software-guard-extensions-remote-attestation-end-to-end-example) for TownCrier enclave

    :::shell
    $ curl -d '{"id": 123, "jsonrpc": "2.0", "method": "attest"}' \
        server.town-crier.org:8123
    {"id":123,"jsonrpc":"2.0","result":"AgABAG4NAAAEAAQAAAAAAIiIiIiIiIiIiIiIiIiIiIgAAAAAAAAAAAAAAAAAAAAABAT//wEBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAABzbbPKy++5Ts5JzgiKEEwAgTpRQfqkNCQ1uN4xSNZI0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACD1xnnferKFHD2uvYqTXdDA8iZ22kCD5xw7h38CMfOngAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQqAIAAILdpDlCK4jEqK+V7CFVXAlqCoM5H8Srrkb4I4zs7zAWxWfeJMZodhRq5UDxEUwYCIFu6VxuSO9KeeWZbBKIser3usUDlxsBlAWiVlMjLkKoGJ5rMT4W8FashifSDoR/qySmAUJWxejSrj7EqqKufLvCzZoRZ4V3KrqkRKitRvAh2jbDswf9uEmYaK68fjDh2sTQIijz43jgFockshF7Uay8VeA5EJc9H2FnTGEPWXctuilaWGMl48iP1RDgzz3WO/Ptd1brJZ1zOhGmbMXqeFqgnJmT9+KuxOSTn1LC3t88UPpItx1v+Tq0EkJT1Y+WI83SqEgor9nUxyVJUEX39N0LIzMYD3OKfghhqmt0lh+F5oWGDNbhTHAZLYqi+Q3sfJKV4gD+P3pmCvVce2gBAADXxVsQnIOefnYNAdFg4N/BC/NEcU3aRQfEemP+a6BlAe9+xZKH6hTY4hF5+aVRl8tJ8XJaOMB8T3FPYzvFZGXkrej11fFf4P7tK7pKTStpnTVKeeCRj+91lAZcD0cNUBh9CuOW0s3SvgoKabKEoPR9lCMdogIoLHUrXn6IN+1BKKnV75wednX34it82U1O4wm4qBcL3ty7zXA7RpfeyVaXMRcDb4bACQhed75ddOhDXcklKeeowAtHL3vbsIKLZSedSp6jud3oavSbmjWzhX71xqVO25+mRxXrO9vn6YDR/s7iSU6OEc/5i+Jz8gt5KSSnuSqJcF8IiJzswAK/IQ+vwQoDPX8Rx8xwMZ4uat2exjY5vXrEz5FroedC7Yt69Z8L9iBUK+3IZ+LpUgrzftuctxCJXYzVaIpheuIi5Lbs/2GhpjninGijI1SCe1G5xJZZMja1hthuHBd9jkCGxDotNjKFOHmU0g5erOy8cEgo8j5a5C1lye2x"}


# Town Crier Scrapers

| Type | Data source | Request | Response | State |
| ---- | ----------- | ------- | -------- | ----- |
| 1 | [Flight departure delay] | Flight information | Flight delay | <i class="checkmark icon"></i> |
| 2 | [Steam exchange] | || encrypted query not supported
| 3 | [Stock ticker] | Stock symbol and date | Closing price | <i class="checkmark icon"></i> |
| 4 | [UPS tracking] | tracking number | State of the package | API not stable |
| 5 | [Coin market price] | Cryptocurrency name | Current exchange rate | <i class="checkmark icon"></i> |
| 6 | [Weather] |

# Query interfaces

## Flight Departure Delay

This scraper returns the departure delay of a given flight.

- **Data source**: <http://flightaware.com/>
- **Input to TC** (64 bytes):
    1. flight number
        - size: 32 bytes
        - type: `string` converted to `bytes32`, right padded with `0`s
        - example: `FJM273` should be `0x464a4d3237330000000000000000000000000000000000000000000000000000`
    2. scheduled departure time in [UNIX epoch time](https://en.wikipedia.org/wiki/Unix_time):
        - size: 32 bytes
        - type: `uint256`, big-endian encoded integer with leading zeros
        - example: `1492100100` should be `0x0000000000000000000000000000000000000000000000000000000058efa404`
- **Return value** : `delay = uint256(respData)`
	- `delay = 0`: flight not departed yet or not delayed
	- `delay > 0 && delay < 2147483643`: flight delay in seconds
	- `delay = 2147483643`: flight cancelled
- **Geth script snippet**:

        ::javascript
        TownCrier.request.sendTransaction(
            1, TC_CALLBACK_ADD, TC_CALLBACK_FID, 0,
            [0x464a4d3237330000000000000000000000000000000000000000000000000000,
            0x0000000000000000000000000000000000000000000000000000000058efa404],
            {value: fee})

## Stock ticker

This scraper returns the closing price of a given stock symbol on a specified date in USD.

- **Data source**: <https://finance.yahoo.com/>
- **Input to TC** (32 bytes):
    1. stock symbol
        - size: 32 bytes
        - type: `string` converted to `bytes32`, right padded with `0`s
        - example: `GOOG` should be `0x474f4f4700000000000000000000000000000000000000000000000000000000`
    2. [UNIX epoch time](https://en.wikipedia.org/wiki/Unix_time) for the date at 00:00 GMT:
        - size: 32 bytes
        - type: `uint256`, big-endian encoded integer with leading zeros
        - example: `1262390400`, standing for Jan 2nd, 2010, should be `0x000000000000000000000000000000000000000000000000000000004b3e8c80`
- **Return value** : `price = uint256(respData)`, the closing price in USD.
- **Geth script snippet**:

        ::javascript
        TownCrier.request.sendTransaction(
            3, TC_CALLBACK_ADD, TC_CALLBACK_FID, 0,
            [0x474f4f4700000000000000000000000000000000000000000000000000000000,
            0x000000000000000000000000000000000000000000000000000000004b3e8c80],
            {value: fee})

## UPS tracking

This scraper returns the status of a UPS package.

- **Data source**: <https://www.ups.com/>
- **Input to TC** (64 bytes):
    1. UPS tracking number
        - size: 32 bytes
        - type: `string` converted to `bytes32`, right padded with `0`s
        - example: `1ZE331480394808282` should be `0x315a453333313438303339343830383238320000000000000000000000000000`
- **Return value** : `status = uint256(respData)`
	- `status = 0`: package not found,
	- `status = 1`: order processed
	- `status = 2`: shipped
	- `status = 3`: in transit
	- `status = 4`: out for delivery
	- `status = 5`: delivered
- **Geth script snippet**:

        ::javascript
        TownCrier.request.sendTransaction(
            4, TC_CALLBACK_ADD, TC_CALLBACK_FID, 0,
            [0x315a453333313438303339343830383238320000000000000000000000000000],
            {value: fee})

## Coin market price

This scraper returns the current exchange rate of the queried cryptocurrency in USD.

- **Data source**: <https://coinmarketcap.com/>
- **Input to TC** (64 bytes):
    1. Cryptocurrency name
        - size: 32 bytes
        - type: `string` converted to `bytes32`, right padded with `0`s
        - example: `bitcoin` should be `0x626974636f696e00000000000000000000000000000000000000000000000000`
- **Return value** : `rate = uint256(respData)`, current exchange rate in USD.
- **Geth script snippet**:

        ::javascript
        TownCrier.request.sendTransaction(
            4, TC_CALLBACK_ADD, TC_CALLBACK_FID, 0,
            [0x626974636f696e00000000000000000000000000000000000000000000000000],
            {value: fee})

## Weather
- To be filled

# Features of Town Crier in the future

* Respond with a delay

	Currently TC could only respond to a query immediately once discover it. The `FlightInsurance` Contract, for example, requires a user to send two separate transactions, calling `insure()` and `request()` respectively, for one query due to this limitation. If TC supports the feature of responding with a delay, a user could buy a policy a certain period ahead the departure time. And within this single transaction, he could use the parameter `timestamp` in the `request()` interface to ask TC not to fetch data from the website until it has come to the scheduled departure time. Only the flight state scraped then matters in this application.

* Encrypted query

	In some applications such as the Steam Trade, a user's account and key is required to access the trade information on the website. Such sensitive data in query should be encrypted before sent to the contract. Currently TC could only process plain data but we expect to add this feature in the near future.

* More websites to suppport

	There are only a few scrapers so applications TC can support are very limited. We look forward to your proposals and designing scrapers and applications for TC!

[Ropsten (Revived)]: https://github.com/ethereum/ropsten/blob/master/revival.md
[here]: https://github.com/ethereum/ropsten
[Flight departure delay]: http://flightaware.com/
[Steam exchange]: http://store.steampowered.com/
[Stock ticker]: https://finance.yahoo.com/
[UPS tracking]: https://www.ups.com/
[Coin market price]: https://coinmarketcap.com/
[Weather]: https://darksky.net
