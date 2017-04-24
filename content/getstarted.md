Title: Get Started
Date: 2017-4-6
toc: yes

# Get Started with Town Crier

Using Town Crier is simple.
To obtain data from a target website, an application contract sends a query to the `TownCrier` Contract, which serves as a front end for TC.
This query consists of the query type, which specifies what kind of data is requsted and the data source, i.e., a trusted website, and some query parameters, namely the specifics of the query to the website.
For example, if the requesting contract is seeking for a stock quote on Oracle Corporation, it might specify that it wants the result of sending ticker 'ORCL' to a trusted website for stock quotes, specifically <https://finance.yahoo.com/> for this application in our TC implementation.

Behind the scenes, when it receives a query from an application contract, the TC server fetches the requested data from the website and relays it back to the requesting contract.
The processing of the query happens inside an SGX-protected environment known as an "enclave".
The requested data is fetched via a TLS connection to the target website that terminates inside the enclave.
SGX protections prevent even the operator of the server from peeking into the enclave or modifying its behavior, while use of TLS prevents tampering or eavesdropping on communications on the network. 
<!-- figure for data flow -->

Town Crier can optionally ingest an <i>encrypted</i> query, allowing it to handle <i> secret query data </i>.
For example, a query could include a password used to log into a server or secret trading data.
TC's operation in an SGX enclave ensures that the password or trading data is concealed from the TC operator (and everyone else). <!-- TBD -->

## Understand the `TownCrier` Contract

The `TownCrier` contract provides a uniform interface for queries from and replies to an application contract, which we also refer to as a "Requester".
This interface consists of the following three functions.

* `request(uint8 requestType, address callbackAddr, bytes4 callbackFID, uint256 timestamp, bytes32[] requestData) public payable returns(uint64);`

	An application contract sends queries to TC by calling function `request()`, and it needs to send the following parameters.
    
    - `requestType`: indicates the query type. You can find the query types and respective formats that Town Crier currently 
    supports on the [Dev page].
    
    - `callbackAddr`: the address of the application contract to which the response from Town Crier is forwarded.
    
    - `callbackFID`: specifies the callback function in the application contract to receive the response from TC.
    
    - `timestamp`: currently unused parameter. This parameter will be used in a future feature.
    Currently TC only responds to requests immediately.
    Eventually TC will support requests with a future query time pre-specified by `timestamp`.
    At present, developers can ignore this parameter and just set it to 0.
    
    - `requestData`: data specifying query parameters.
    The format depends on the query type.

    When the `request` function is called, a request is logged by event `RequestInfo()`.
    The function returns a `requestId` that is uniquely assigned to this request.
    The application contract can use the `requestId` to check the response or status of a request in its logs.
    The Town Crier server watches events and processes a request once logged by `RequestInfo()`. 
    
    Requesters must prepay the gas cost incurred by the Town Crier server in relaying a response to the application contract.
    `msg.value` is the amount of wei a requester pays and is recorded as `Request.fee`.
    
* `deliver(uint64 requestId, bytes32 paramsHash, uing64 error, bytes32 respData) public;`
    
    After fetching data and generating the response for the request with `requestId`, TC sends a transaction calling function `deliver()`. 
    `deliver()` verifies that the function call is made by SGX and that the hash of query parameters is correct.
    Then it calls the callback function of the application contract to transmit the response. 
   
    The response includes `error` and `respData`.
    If `error = 0`, the application contract request has been successfully processed and the application contract can then safely use `respData`.
    The fee paid by the application contract for the request is consumed by TC.
    If `error = 1`, the application contract request is invalid or cannot be found on the website.
    In this case, similarly, the fee is consumed by TC. 
    If `error > 1`, then an error has occured in the Town Crier server.
    In this case, the fee is fully refunded but the transaction cost for requesting by the application contract won't be compensated. 
    
* `cancel(uint64 requestId) public returns(bool);`
    
    A requester can cancel a request whose response has not yet been issued by calling function `cancel()`.
    `requestId` is required to specify the query. 
    The fee paid by the Appliciation Contract is then refunded (minus processing costs, denoted as cancellation fee). 

For more details, you can look at the source code of the contract [TownCrier.sol].

## Reference Application Contract for TC

### An application contract for general requesting and responding

To show how to interface with the `TownCrier` Contract, we present a skeleton `Application` Contract that does nothing other than sending queries, logging responses and cancelling queries.

First, you need to annotate your contract with the version pragma:
```
pragma solidity ^0.4.9;
```
For [Mist] users, the current stable version of Mist only supports solidity ^0.4.8. 

Second, you need to include in your contract source code the function declaration headers of the `TownCrier` Contract so that the application contract can call those functions with the address of the `TownCrier` Contract.
```
contract TownCrier {
    function request(uint8 requestType, address callbackAddr, bytes4 callbackFID, uint timestamp, bytes32[] requestData) public payable returns (uint64);
    function cancel(uint64 requestId) public returns (bool);
}
```

Third, let's look at the layout of the `Application` Contract:
```
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
```
* The events `Request()`, `Response` and `Cancel()` keeps logs of the `requestId` assigned to a query, the response from TC and the result of a cancellation respectively for a user to fetch from the blockchain.
* The constant `TC_CALLBACK_FID` is the first 4 bytes of the hash of the function `response()` that the `TownCrier` Contract calls when relaying the response from TC. The name of the callback function can differ but the three parameters should be exactly the same as in this example.
* The address array `requesters` stores the addresses of the requesters.
* The uint array `fee` stores the amounts of wei requesters pay for their queries.

As you can see above, the `Application` Contract consists of a set of five basic functions:

* `function() public payable;`

    This fallback function must be payable so that TC can provide a refund under certain conditions.
    The fallback function should not cost more than 2300 gas, otherwise it will run out of gas when TC refunds ether to it.
    In our contract, it simply does nothing.
	```
	function() public payable {}
	```
    
* `function Application(TownCrier tc) public;`
    
    This is the constructor which registers the address of the TC Contract and the owner of this contract during creation so that it can call the `request()` and `cancel()` functions in the TC contract.
    
	```
	TownCrier public TC_CONTRACT;
	address owner; // creator of this contract

	function Application(TownCrier tcCont) public {
		TC_CONTRACT = tcCont;
		owner = msg.sender;
	}
	```
	The address of the TC Contract is on the [Dev page]. Our current deployment on the Ropsten Testnet (Revived Chain) is `0xC3847C4dE90B83CB3F6B1e004c9E6345e0b9fc27`.
    
* `function request(uint8 requestType, bytes32[] requestData) public payable;`
    
    A user calls this function to send a request to the `Application` Contract. is to call `request()` in the TC Contract.
    `TC_CALLBACK_ADD` is the address of the fallback function. If this line is in the same contract as the callback function, then `TC_CALLBACK_ADD` could simply be replaced by `this`.
    `TC_CALLBACK_FID` should be hardcoded as the first 4 bytes of the hash of the callback function specification.
	```
	function request(uint8 requestType, bytes32[] requestData) public payable {
        if (msg.value < TC_FEE) {
            if (!msg.sender.send(msg.value)) {
                throw;
            }
            Request(-1, msg.sender, requestData.length, requestData);
            return;
        }

        uint64 requestId = TC_CONTRACT.request.value(msg.value)(requestType, this, TC_CALLBACK_FID, 0, requestData);
        if (requestId == 0) {
            if (!msg.sender.send(msg.value)) { 
                throw;
            }
            Request(-2, msg.sender, requestData.length, requestData);
            return;
        }
        
        requesters[requestId] = msg.sender;
        fee[requestId] = msg.value;
        Request(int64(requestId), msg.sender, requestData.length, requestData);
    }
	```
	
    Developers need to be careful with the fee sent with the function call.
    TC requires at least <b>3e4</b> gas for all the operations other than forwarding the response to the `Application` Contract in `deliver()` function and the gas price is set as <b>5e10 wei</b>.
    So a requester should pay no less than <b>1.5e15 wei</b> for one query. Otherwise the `request` call will fail and the TC Contract will return 0 as `requestId`.
    Developers should deal with this case separately.
    In the TC Contract, the gas limit for calling the callback function in the `Application` Contract is bounded by the fee a requester paid originally when sending the query.
    If the callback function costs about 2e4 gas, for example, the least fee to be paid for one query should be (3e4 + 2e4) * 5e10 = 2.5e15 wei.
    In addition, TC server sets the gas limit as <b>3e6</b> when sending a transaction to `deliver()` function in the TC Contract.
    If a requester paid more gas cost than the transaction allows, the excess ether cannot be used for the callback function. It will go directly to the SGX wallet. This is a way to offer a tip for the Town Crier service.

* `function response(uint64 requestId, uint64 error, bytes32 respData) public;`

	This is the function which will be called by the TC Contract to deliver the response from TC server.
    The specification `TC_CALLBACK_FID` for it should be hardcoded as `bytes4(sha3("response(uint64,uint64,bytes32)"))`.
	```
	function response(uint64 requestId, uint64 error, bytes32 respData) public {
        if (msg.sender != address(TC_CONTRACT)) {
            Response(-1, msg.sender, 0, 0); 
            return;
        }

        address requester = requesters[requestId];
        requesters[requestId] = 0;

        if (error < 2) {
            Response(int64(requestId), requester, error, uint(respData));
        } else {
            requester.send(fee[requestId]);
            Response(int64(requestId), msg.sender, error, 0);
        }
    }
	```
    
    Since the gas limit for sending a response back to the TC Contract is set as <b>3e6</b> by the Town Crier server, as mentioned above, the callback function should not consume more gas than this. Otherwise the callback function will run out of gas and fail.
    The TC service does not take responsibility for such failures, and treats queries that fail in this way as successfully responded to.
    We suggest the application contract developers set a lower bound for the request fee such that the callback function won't run out of gas when receiving and processing responses from TC.

* `TownCrier.cancel(requestId);`

	This line is for cancellation, calling the `cancel()` function in the TC Contract.
	```
	function cancel(uint64 requestId) public {
        if (requestId == 0 || requesters[requestId] != msg.sender) {
            // If the requestId is invalid or the requester is not the message sender,
            // cancellation fails.
            Cancel(requestId, msg.sender, false);
            return;
        }

        bool tcCancel = TC_CONTRACT.cancel(requestId); // calling cancel() in the TownCrier Contract
        if (tcCancel) {
            // Successfully cancels the request in the TownCrier Contract,
            // then refund the requester with (fee - cancellation fee).
            requesters[requestId] = 0;
            if (!msg.sender.send(fee[requestId] - CANCELLATION_FEE)) {
                Cancel(requestId, msg.sender, false);
                throw;
            }
            Cancel(requestId, msg.sender, true);
        } else {
            // Cancellation in the TownCrier Contract fails.
            Cancel (requestId, msg.sender, false);
        }
    }
	```
    A developer must carefully set a cancelled flag for the request before refunding the requester in order to prevent reentrancy attacks.

You can look at [Application.sol] for the complete `Application` Contract logic required to interface with TC.

### A practical flight insurance contract

The `Application` Contract above is only able to send queries to and receive responses from TC.
For many real-life applications there is one critical factor missing: <b>timing</b>.
A stock exchange contract which settles at a specified time needs to know the stock quote for that time.
A trip insurance contract which needs to find out whether a flight departs on time must fetch the flight state after the scheduled departure time.
A contract for the sale of a physical good has to wait for a period for delivery after payment to check whether the good was successfully delivered.
The immediate response TC currently supports cannot directly fulfill such requirements in these applications, but
developers can use other strategies to get around this limitation. (Future versions of TC will allow for pre-specified, future query times using the `timestamp` parameter.)

Here we present a design for a flight insurance application that illustrates use of the full existing range of TC features.

#### Application setting

Suppose Alice wants to set up a flight insurance service in the form of a smart contract `FlightInsurance`.
A user can buy a policy for her flight by sending money to the `FlightInsurance` Contract.
`FlightInsurance` offers a payout to the user should her insured flight be delayed or cancelled.
(Unfortunately, TC cannot detect whether you've been senselessly beaten and dragged off your flight by United Airlines.) 

#### Problem with the `Application` Contract

The `FlightInsurance` Contract contains the same five basic components found above in the `Application` Contract.
However, we don't want to query TC immediately after a user, say Bob, purchases a policy. If we do so, this will result in one of two inappropriate cases.
One is that Bob purchases a policy for a flight that has already been delayed or cancelled, which is unfair to Alice.
The other is that Bob purchases a policy before the scheduled departure time of his flight so when the `FlightInsurance` Contract queries immediately, it will get response of "not delayed" since the flight hasn't yet left. This is unfair to Bob.

#### A scheme to get around the problem

To address this problem, we can separate the two operations and deal with them at different times.
The `FlightInsurance` Contract needs to include a `Insure()` function for a user to buy a policy for his flight a certain period ahead of the scheduled departure time, say 24 hours.
The contract can simply compare `block.timestamp` with the flight data to guarantee this restriction.
If the request is valid, then the contract will store the flight data and issue a policy ID to the user for querying TC later.
When the flight departs, the user can send a transaction to `Request()` with the policy ID in the `FlightInsurance` Contract, and the contract will query TC.
Then everything works much as in the `Application` Contract.

You can take a look at [FlightInsurance.sol] for the complete `FlightInsurance` Contract logic.

[Mist]: https://github.com/ethereum/mist
[Dev page]: http://www.town-crier.org/staging/dev.html
[TownCrier.sol]: code/TownCrier.sol
[Application.sol]: code/Application.sol
[FlightInsurance.sol]: code/FlightInsurance.sol
