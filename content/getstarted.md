Title: Getting Started
Date: 2017-4-6
toc: yes
slug: get-started

# Using Town Crier in Your Smart Contracts

There are two convenient ways to use Town Crier in your smart contracts.

## Option A: Using SmartContract.com

SmartContract.com's [TC-backed-oracle creation tool](https://create.smartcontract.com/#/choose) is a nice, easy way to get started with Town Crier in just a few minutes. Today, this tool is only available for cryptocurrency prices.

We ask that you define the method which Town Crier will be sending to as shown below. You should then be all set to quickly set up a TC-backed oracle in the SmartContract.com environment. Here is an example of what your Town Crier Oracle will look like when it goes live: [https://staging.smartcontract.com/#/contracts/4bd8ecf48f87bf423c5a7c82e327c239](https://staging.smartcontract.com/#/contracts/4bd8ecf48f87bf423c5a7c82e327c239).

### Writing a smart contract function to work with Town Crier:

To receive a response from TC, the requester need to specify the recipient contract as well as the recipient interface. Very importantly, TC requires the recipient function to have the following signature:

```javascript
function FUNCTION_NAME(uint64 requestId, uint64 error, bytes32 respData) public;
```

This is the function which will be called by the TC Contract to deliver the response from TC server. The specification for it should be hardcoded as `bytes4(sha3("FUNCTION_NAME(uint64,uint64,bytes32)"))` and is passed in as `callbackFID` when calling `request()` function of the TC Contract. Details about how to test if your function is written correctly can be found [here](#callbackFID).

## Option B: Interfacing with TC directly

Interfacing directly with Town Crier requires a little more work, but is also straightforward, and gives access to all of TC's currently supported set of data types.
To query one of the [supported data sources](dev.html), an application contract just needs to send a query to the `TownCrier` Contract, which lives on the [mainnet](XXX).

A query consists of a _query type_, which specifies the data source to be queried and some _parameters_,
along with a callback address to which the data feeds will be delivered.
For example, if your contract is seeking for a stock quote on the Oracle Corporation, it can simply query with type `3` (i.e. the Yahoo! Finance) and parameter `ORCL` (i.e. the ticker). Supported data sources are listed [here](dev.html). Keep in mind that we're still actively adding more to the list.

Once the query is processed by the TC server, the `TownCrier` Contract will deliver the resulting data to the callback address specified in the request. It does this by sending an inter-contract message.

For an end-to-end example, you can jump to [Step-by-step: Developing Your First TC-aware Contract](#Step-by-Step).

# How Town Crier Works: The Big Picture

<img class="ui medium centered image" src="theme/images/1.png"></img>

Behind the scenes, when it receives a query from an application contract, the TC server fetches the requested data from the website and relays it back to the requesting contract.
Query processing happens inside an SGX-protected environment known as an "enclave".
The requested data is fetched via a TLS connection to the target website that terminates inside the enclave.
SGX protections prevent even the operator of the server from peeking into the enclave or modifying its behavior, while use of TLS prevents tampering or eavesdropping on communications on the network.

<img class="ui medium centered image" src="theme/images/2.png"></img>

Town Crier can optionally ingest an <i>encrypted</i> query, allowing it to handle <i> secret query data </i>.
For example, a query could include a password used to log into a server or secret trading data.
TC's operation in an SGX enclave ensures that the password or trading data is concealed from the TC operator (and everyone else).

# Step-by-Step: Developing Your First TC-Aware Contract
<a name="Step-by-Step"></a>

## The TC interface

To use TC, you'll need two functions exposed by the `TownCrier` contract.

### Sending a request: `request`

```javascript
request(uint8 requestType, address callbackAddr, \
        bytes4 callbackFID, uint256 timestamp, \
        bytes32[] requestData) public payable returns(uint64);
```

An application contract sends queries to TC by calling function `request()` with following parameters.

- `requestType`: indicates the query type. Should be one of the [supported query types](dev.html).
- `callbackAddr`: the address of the recipient contract.
- `callbackFID`: the callback function selector.
- `timestamp`: reserved. Unused for now.
- `requestData`: data specifying query parameters. The format depends on the query type.

When the `request` function is called, a request is logged by event `RequestInfo()`.
The function returns a `requestId` that is uniquely assigned to this request.
The application contract can use the `requestId` to check the response or status of a request in its logs.
The Town Crier server watches events and processes a request once logged by `RequestInfo()`.

Requesters must prepay the gas cost incurred by the Town Crier server in relaying a response to the application contract. `msg.value` is the amount of `wei` a requester pays and is recorded as `Request.fee`.



<!--
```javascript
deliver(uint64 requestId, bytes32 paramsHash, \
        uint64 error, bytes32 respData) public;
```

After fetching data and generating the response for the request with `requestId`, TC sends a transaction calling function `deliver()`.
`deliver()` verifies that the function call is made by SGX and that the hash of query parameters is correct.
Then it calls the callback function of the application contract to transmit the response.


-->

### Canceling a request: `cancel`

```javascript
cancel(uint64 requestId) public returns(bool);
```

Unprocessed requests can be canceled by calling function `cancel(requestId)`.
The fee paid by the requester is then refunded (minus processing costs, denoted as cancellation fee).

For more details about how Town Crier contract works, you can look at the source code of the contract [TownCrier.sol].

### Receiving a response
<a name="callbackFID"></a>

To receive a response from TC, the requester need to specify the recipient contract as well as the recipient interface.
Very importantly, TC requires that the recipient function to have the following signature:

```javascript
function FUNCTION_NAME(uint64 requestId, uint64 error, bytes32 respData) public;
```

This is the function which will be called by the TC Contract to deliver the response from TC server.
The specification for it should be hardcoded as `bytes4(sha3("FUNCTION_NAME(uint64,uint64,bytes32)"))` and is passed in as `callbackFID` when calling `request()` function of the TC Contract.

The response includes `error` and `respData`.
If `error = 0`, the application contract request has been successfully processed and the application contract can then safely use `respData`.
The fee paid by the application contract for the request is consumed by TC.
If `error = 1`, the application contract request is invalid or cannot be found on the website.
In this case, similarly, the fee is consumed by TC.
If `error > 1`, then an error has occured in the Town Crier server.
In this case, the fee is fully refunded but the transaction cost for requesting by the application contract won't be compensated.

## An example contract

To show how to interface with the `TownCrier` Contract, we present a skeleton `Application` Contract that does nothing other than sending queries, logging responses and cancelling queries.

First, you need to annotate your contract with the version pragma:

	pragma solidity ^0.4.9;

For [Mist] users, the current stable version of Mist only supports solidity ^0.4.8.

Second, you need to include in your contract source code the function declaration headers of the `TownCrier` Contract so that the application contract can call those functions with the address of the `TownCrier` Contract.

	contract TownCrier {
	    function request(uint8 requestType, address callbackAddr, bytes4 callbackFID, uint timestamp, bytes32[] requestData) public payable returns (uint64);
	    function cancel(uint64 requestId) public returns (bool);
	}

You don't need to include `response()` here because an appilcation contract should not make a function call to it but wait for being called by it.

Third, let's look at the layout of the `Application` Contract:

	contract Application {
	    event Request(int64 requestId, address requester, uint dataLength, bytes32[] data);
	    event Response(int64 requestId, address requester, uint64 error, uint data);
	    event Cancel(uint64 requestId, address requester, bool success);

	    bytes4 constant TC_CALLBACK_FID = bytes4(sha3("response(uint64,uint64,bytes32)"));

	    address[2**64] requesters;
	    uint[2**64] fee;

	    function() public payable;
	    function Application(TownCrier tcCont) public;
	    function request(uint8 requestType, bytes32[] requestData) public payable;
	    function response(uint64 requestId, uint64 error, bytes32 respData) public;
	    function cancel(uint64 requestId) public;
	}

* The events `Request()`, `Response` and `Cancel()` keeps logs of the `requestId` assigned to a query, the response from TC and the result of a cancellation respectively for a user to fetch from the blockchain.
* The constant `TC_CALLBACK_FID` is the first 4 bytes of the hash of the function `response()` that the `TownCrier` Contract calls when relaying the response from TC. The name of the callback function can differ but the three parameters should be exactly the same as in this example.
* The address array `requesters` stores the addresses of the requesters.
* The uint array `fee` stores the amounts of wei requesters pay for their queries.

As you can see above, the `Application` Contract consists of a set of five basic functions:

* `function() public payable;`

	This fallback function must be payable so that TC can provide a refund under certain conditions.
    The fallback function should not cost more than 2300 gas, otherwise it will run out of gas when TC refunds ether to it.

		function() public payable {}

    In our contract, it simply does nothing.

* `function Application(TownCrier tc) public;`

    This is the constructor which registers the address of the TC Contract and the owner of this contract during creation so that it can call the `request()` and `cancel()` functions in the TC contract.

		TownCrier public TC_CONTRACT;
		address owner;

		function Application(TownCrier tcCont) public {
			TC_CONTRACT = tcCont;
			owner = msg.sender;
		}

	The address of the TC Contract is on the [Dev page].
	Our current deployment on the Ropsten Testnet (Revived Chain) is `0xC3847C4dE90B83CB3F6B1e004c9E6345e0b9fc27`.

* `function request(uint8 requestType, bytes32[] requestData) public payable;`

    A user calls this function to send a request to the `Application` Contract.
	This function forwards the query to `request()` of the TC Contract by
	`requestId = TC_CONTRACT.request.value(msg.value)(requestType, TC_CALLBACK_ADD, TC_CALLBACK_FID, timestamp, requestData);`.

	`msg.value` is the fee the user pays for this request.
	`TC_CALLBACK_ADD` is the address of the fallback function.
	If this line is in the same contract as the callback function, then `TC_CALLBACK_ADD` could simply be replaced by `this`.
    `TC_CALLBACK_FID` should be hardcoded as the first 4 bytes of the hash of the callback function specification, as defined above.

		uint constant MIN_GAS = 30000 + 20000;
		uint constant GAS_PRICE = 5 * 10 ** 10;
		uint constant TC_FEE = MIN_GAS * GAS_PRICE;

		function request(uint8 requestType, bytes32[] requestData) public payable {
			if (msg.value < TC_FEE) {
				// If the user doesn't pay enough fee for a request,
				// we should discard the request and return the ether.
				if (!msg.sender.send(msg.value)) throw;
				return;
			}

			uint64 requestId = TC_CONTRACT.request.value(msg.value)(requestType, this, TC_CALLBACK_FID, 0, requestData);
			if (requestId == 0) {
				// If the TC Contract returns 0 indicating the request fails
				// we should discard the request and return the ether.
				if (!msg.sender.send(msg.value)) throw;
				return;
			}

			// If the request succeeds,
			// we should record the requester and how much fee he pays.
			requesters[requestId] = msg.sender;
			fee[requestId] = msg.value;
			Request(int64(requestId), msg.sender, requestData.length, requestData);
		}

    Developers need to be careful with the fee sent with the function call.
    TC requires at least <b>3e4</b> gas for all the operations other than forwarding the response to the `Application` Contract in `deliver()` function and the gas price is set as <b>5e10 wei</b>.
    So a requester should pay no less than <b>1.5e15 wei</b> for one query. Otherwise the `request` call will fail and the TC Contract will return 0 as `requestId`.
    Developers should deal with this case separately.
    In the TC Contract, the gas limit for calling the callback function in the `Application` Contract is bounded by the fee a requester paid originally when sending the query.
    For example, in our contract the callback function costs about 2e4 gas, so the least fee to be paid for one query
	should be (3e4 + 2e4) * 5e10 = 2.5e15 wei, denoted as `TC_FEE`.
    In addition, TC server sets the gas limit as <b>3e6</b> when sending a transaction to `deliver()` function in the TC Contract.
    If a requester paid more gas cost than the transaction allows, the excess ether cannot be used for the callback function. It will go directly to the SGX wallet. This is a way to offer a tip for the Town Crier service.

* `function response(uint64 requestId, uint64 error, bytes32 respData) public;`

	This is the function which will be called by the TC Contract to deliver the response from TC server.
    The specification `TC_CALLBACK_FID` for it should be hardcoded as `bytes4(sha3("response(uint64,uint64,bytes32)"))`.

		function response(uint64 requestId, uint64 error, bytes32 respData) public {
			// If the response is not sent from the TC Contract,
			// we should discard the response.
    	    if (msg.sender != address(TC_CONTRACT)) return;

    	    address requester = requesters[requestId];
    	    // Set the request state as responded.
			requesters[requestId] = 0;

    	    if (error < 2) {
				// If either TC responded with no error or the request is invalid by the requester's fault,
				// public the response on the blockchain by event Response().
    	        Response(int64(requestId), requester, error, uint(respData));
    	    } else {
				// If error exists by TC's fault,
				// fully refund the requester.
    	        requester.send(fee[requestId]);
    	        Response(int64(requestId), msg.sender, error, 0);
    	    }
    	}

    Since the gas limit for sending a response back to the TC Contract is set as <b>3e6</b>
	by the Town Crier server, as mentioned above, the callback function should not consume more gas than this.
	Otherwise the callback function will run out of gas and fail.
    The TC service does not take responsibility for such failures, and treats queries that fail in this way as successfully responded to.
    We suggest the application contract developers set a lower bound for the request fee
	so that the callback function won't run out of gas when receiving and processing responses from TC.
	To estimate how much gas the callback function costs, you can use Javascript API [web3.eth.estimateGas].

* `function cancel(uint64 requestId) public;`

	This function is for cancellation, calling the `cancel()` function in the TC Contract.

		uint constant CANCELLATION_FEE = 25000 * GAS_PRICE;

		function cancel(uint64 requestId) public {
			// If the cancellation request is not sent by the requester himself,
			// discard the cancellation request.
    	    if (requestId == 0 || requesters[requestId] != msg.sender) return;

    	    bool tcCancel = TC_CONTRACT.cancel(requestId);
    	    if (tcCancel) {
				// If the cancellation succeeds,
				// set the request state as cancelled and partially refund the requester.
    	        requesters[requestId] = 0;
    	        if (!msg.sender.send(fee[requestId] - CANCELLATION_FEE)) throw;
    	        Cancel(requestId, msg.sender, true);
    	    }
    	}

	TC charges <b>2.5e4 * 5e10 = 1.25e15</b> wei, denoted as `CANCELLATION_FEE` here, for cancelling an unresponded query.
	In this function a user is partially refunded `fee - CANCELLATION_FEE`.
	A developer must carefully set a cancelled flag for the request before refunding the requester in order to prevent reentrancy attacks.

You can look at [Application.sol] for the complete `Application` Contract logic required to interface with TC.

## Send some queries!

Let's actually send some queries from the `Application` contract TC.
To begin with, you need to deploy the contract to testnet (or main net).
[Ethereum greeter tutorial] provides thorough introduction to installing the solidity compiler and deploying smart contracts.
Here assume you already deployed the contract and has an instance of it called `instance`:

```javascript
var instance = contract.at('0xdeadbeef');
```

Let's try to query for flight departure delays. Below is an excerpt of the [Dev page]:

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

The interface is straightforward to use, with the only caveat that
you must get the padding right.
You have at least three options to pad parameters in `geth`.

**Option 1: do it mannually!**

```javascript
instance.request.sendTransaction(1,
    [0x464a4d3237330000000000000000000000000000000000000000000000000000,
    0x0000000000000000000000000000000000000000000000000000000058efa404],
    {from: eth.defaultAccount, value: 3e15, gas: 3e6});
```

**Option 2: write a helper function**

The encoded parameters seem messy.
You can use the following script to pad the departure time into 32 bytes automatically:

```
function pad(n, width) {
    m = n.toString(16);
    return '0x' + new Array(width - m.length + 1).join('0') + m;
}

instance.request.sendTransaction(1, ["FJM273", pad(1492100100, 64)],
	{from: eth.defaultAccount, value: 3e15, gas: 3e6});
```

**Option 3: let `geth` deal with it**

You may also modify the function `request()` of the application contract a little bit
so that users don't have to deal with the encodings of request data:

```javascript
function request(uint8 requestType, bytes32 flightNumber, uint flightTime) public payable {
	bytes32[] memory requestData = new bytes32[](2);
	requestData[0] = flightNumber;
	requestData[1] = bytes32(flightTime);

	// The same as the original version follows...
}
```

With the interface above, a user could simply make a request by the following script:

```javascript
instance.request.sendTransaction(1, "FJM273", 1492100100,
	{from: eth.defaultAccount, value: 3e15, gas: 3e6});
```

Okay, by now you've successfully created a TC-aware smart contract.
One last tip for debugging:
you can [watch events] `Request()` and `Response()` of the application contract to get assigned `requestId` and response from TC for a query.

# More Practical Examples

While the above example demonstrates the basic usage of TC, it is of limited
capability. We've also developed several other full-blown examples to showcase
the power of TC.
You can read more [here](XXX).


[Mist]: https://github.com/ethereum/mist
[Dev page]: http://www.town-crier.org/staging/dev.html
[TownCrier.sol]: code/TownCrier.sol
[Application.sol]: code/Application.sol
[FlightInsurance.sol]: code/FlightInsurance.sol
[web3.eth.estimateGas]: https://github.com/ethereum/wiki/wiki/JavaScript-API#web3ethestimategas
[Ethereum greeter tutorial]: https://www.ethereum.org/greeter
[watch events]: https://github.com/ethereum/wiki/wiki/JavaScript-API#contract-events
