Title: Dev Info
Date: 2017-4-6
toc: yes

# Adress of the `TownCrier` Contract
<! tc address>

# Request types Town Crier currently support and formats

| Type | Data source | Request | Response |
| ---- | ----------- | ------- | -------- |
| 1 | [Flight departure delay] | Flight information | Flight delay |
| 2 | [Steam exchange] | 
| 3 | [Stock ticker] | Stock symbol and date | Closing price |
| 4 | [UPS tracking] | UPS tracking number | State of the package |
| 5 | [Coin market price] | Cryptocurrency type | Current exchange rate |
| 6 | [Weather] |


<ol>
<li>Flight departure delay</li>
Request: [flight number, scheduled departure time in UNIX epoch time]

* flight number: string converted to bytes32, right padded with 0s
* scheduled departure time in UNIX epoch time: uint converted to bytes32, padded with leading 0s

Response: delay

Example: `TownCrier.request(1, TC_CALLBACK_ADD, TC_CALLBACK_FID, 0, [])`

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
