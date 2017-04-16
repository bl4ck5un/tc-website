Title: Dev Info
Date: 2017-4-6
slug: dev
toc: yes

# Adress of the `TownCrier` Contract
<! tc address>

# Town Crier Scrapers

Say something about scrapers. Maybe some diagrams.

## Flight Departure Delay

This scraper returns if a given flight is delayed based on the data from `www.flightaware.com`.

- **Data source**: `www.flightaware.com`
- **Input to TC** (64 bytes): 
    1. flight number
        - size: 32 bytes
        - type: `string` converted to `bytes32`, right padded with `0`s
        - example: `FJM273` should be converted to `0x464a4d3237330000000000000000000000000000000000000000000000000000`
    2. scheduled departure time in [UNIX epoch time](https://en.wikipedia.org/wiki/Unix_time): 
        - size: 32 bytes
        - type: `uint256` (big-endian encoded integer with leading zeros)
        - example: `1492100100` should be `0x0000000000000000000000000000000000000000000000000000000058efa404`
- **Return value:** `(error, delay)`
    1. error: `uint256`.
    2. delay: `uint256`, 0 or 1 indicating if the flight is delayed.
- **Full example**: `TownCrier.request(1, TC_CALLBACK_ADD, TC_CALLBACK_FID, 0, [0x464a4d3237330000000000000000000000000000000000000000000000000000, 0x0000000000000000000000000000000000000000000000000000000058efa404])`


<ol>
<li>Steam exchange</li>
    
<li>Stock ticker</li>
Request: [stock symbol, date]

Response: 

<li>UPS tracking</li>
Request: [UPS tracking number]

* UPS tracking number: string converted to bytes32, padded with

Response:

<li>Coin market price</li>
Request: []
    
<li>Weather</li>
</ol>


# Features of Town Crier in the future

* Respond with a delay
* Encrypted query
* More websites to suppport


[Flight departure delay]: http://flightaware.com/
[Steam exchange]: http://store.steampowered.com/
[Stock ticker]: https://finance.yahoo.com/
[UPS tracking]: https://www.ups.com/
[Coin market price]: https://coinmarketcap.com/
[Weather]: https://darksky.net
