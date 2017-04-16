Title: Get Started
Date: 2017-4-6
Category: Tutorial


# Get Started with Town Crier

Using Town Crier is simple.
To obtain data from a target website, an application contract sends a query to the `TownCrier` Contract, which serves as a front end for TC.
This query consists of the query type, which specifies what kind of data is requsted and the data source, i.e., a trusted website, and some query parameters, namely the specifics of the query to the website.
For example, if the requesting contract is seeking for the a stock quote on Oracle Corporation, it might specify that it wants the result of sending ticker 'ORCL' to a trusted website for stock quotes, specifically <https://finance.yahoo.com/> for this application in our TC implementation.

Behind the scenes, when it receives a query from an application contract, the TC server fetches the requested data from the website and relays it back to the requesting contract.
The processing of the query happens inside an SGX-protected environment known as an "enclave".
The requested data is fetched via a TLS connection to the target website that terminates inside the enclave.
SGX protections prevent even the operator of the server from peeking into the enclave or modifying its behavior, while use of TLS prevents tampering or eavesdropping on communications on the network. 

Town Crier can optionally ingest an <i>encrypted</i> query, allowing it to handle <i> secret query data </i>.
For example, a query could include a password used to log into a server or secret trading data.
TC's operation in an SGX enclave ensures that the password or trading data is concealed from the TC operator (and everyone else).

## Understand the `TownCrier` Contract

The `TownCrier` contract provides a uniform interface for queries from and replies to an application contract, which we also refer to as a "Requester".
This interface consists of the following three functions.

* `request(uint8 requestType, address callbackAddr, bytes4 callbackFID, uint256 timestamp, bytes32[] requestData) public payable returns(uint64);`

	For an application contract to call function `request()`, it needs to send in the following parameters.
    
    - `requestType`: the type of the query, for the Town Crier server to process it accordingly.
    You'll see all the query types Town Crier currently supports in the following.
    
    - `callbackAddr`: the address of the application contract to which the response from Town Crier is forwarded.
    
    - `callbackFID`: specification of the callback function in the application contract to receive the response from TC.
    
    - `timestamp`: parameter required for a potential feature.
    Currently TC only responds to requests immediately.
    Eventually TC will support requests with pre-specified future query times.
    At present, developers can ignore this parameter and just set it to 0.
    
    - `requestData`: data specifying query parameters.
    The format depends on the query type.

    When this function is called, a request is logged by event `RequestInfo()`.
    The function returns a `requestId` that is uniquely assigned to this request.
    The application contract can use the `requestId` to check the response or status of a request in its logs.
    The Town Crier server watches events and processes a request once logged by `RequestInfo()`. 
    
    Requesters must prepay the gas cost incurred by the Town Crier server in relaying a response to the application contract.
    `msg.value` is the amount of wei a requester pays and recorded as `Request.fee`.
    
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
    
    A requester can cancel a request whose response has not yet been issued. 
    The fee paid by the Appliciation Contract is then refunded (minus processing costs, denoted as cancellation fee). 

For more details, you can look at the source code of the contract [TownCrier.sol].

## Reference Application Contract for TC

### An application contract for general requesting and responding

To show how to interface with the `TownCrier` Contract, we present an `Application` Contract that does nothing othan than sending queries, logging responses and cancelling queries. It consists of a set of five basic components:

* `function() public payable;`

    This fallback function must be payable so that TC can provide a refund under certain conditions.
    The fallback function should not cost more than 2300 gas, otherwise it will run out of gas when TC refunds ether to it.
    
* `function Application(TownCrier tc) public;`
    
    The `Application` Contract needs to store the address of the TC Contract during creation so that it can call the `request()` and `cancel()` functions in the TC contract.
    
    <b>The address of the TC Contract is <! TC address ></b>
    
* `requestId = TownCrier.request.value(fee)(requestType, TC_CALLBACK_ADD, TC_CALLBACK_FID, 0, requestData);`
    
    This line is to call `request()` in the TC Contract.
    `TC_CALLBACK_ADD` is the address of the fallback function. If this line is in the same contract as the callback function, then `TC_CALLBACK_ADD` could simply be replaced by `this`.
    `TC_CALLBACK_FID` should be hardcoded as the first 4 bytes of the hash of the callback function specification.
    
    Developers need to be careful with the fee sent with the function call.
    TC requires at least <b>3e4</b> gas for all the operations other than forwarding the response to the `Application` Contract in `deliver()` function and the gas price is set as <b>5e10 wei</b>.
    So a requester should pay no less than <b>1.5e15 wei</b> for one query otherwise the `request` call would fail and the TC Contract would return 0 as `requestId`.
    Developers should deal with this case separately.
    In the TC Contract, the gas limit for calling the callback function in the `Application` Contract is bounded by the fee a requester paid originally when sending the query.
    If the callback function costs about 2e4 gas, for example, the least fee to be paid for one query should be (3e4 + 2e4) * 5e10 = 2.5e15 wei.
    In addition, TC server sets the gas limit as <b>3e6</b> when sending a transaction to `deliver()` function in the TC Contract.
    If a requester paid too much for gas cost than the transaction allows, the excess ether cannot be used for operations of the callback function but will go directly to the SGX wallet, just like tips for Town Crier service.

* `function response(uint64 requestId, uint64 error, bytes32 respData) public;`

	This is the function which will be called by the TC Contract to deliver the response from TC server.
    The specification `TC_CALLBACK_FID` for it should be hardcoded as `bytes4(sha3("response(uint64,uint64,bytes32)"))`.
    
    Since the gas limit for sending a response back to the TC Contract is set as <b>3e6</b> by Town Crier server, as mentioned above, the callback function should not be so complicated that might cost more gas than permitted. Otherwise the callback function would run out of gas and fail.
    TC won't be responsible for such failure and will set the query as responded.
    We suggest the application contract developers set a lowerbound for request fee such that the callback function won't run out of gas when receiving and processing response from TC.

* `TownCrier.cancel(requestId);`

	This line is for cancellation, calling the `cancel()` function in the TC Contract.
    A developer need to carefully set up the cancelled flag for the request before refunding the requester in order to prevent reentrant attacks.

You can look at [Application.sol] for the complete `Application` Contract logic required to interface with TC.

### A practical flight insurance contract

The `Application` Contract above is only able to send queries to and receive responses from TC.
For many real-life applications there is one critical factor missing: <b>timing</b>.
A stock exchange contract which settles the exchange at a specified time needs to know the stock quote for that time.
A trip insurance contract which needs to find out whether a flight departs on time must fetch the flight status after the scheduled departure time.
A contract for the sale of a physical good has to wait for a period for delivery after payment to check whether the good was successfully delivered.
The immediate response TC currently supports cannot fulfill such requirements in these applications.
So developers need to use other strategies to get around this limitation.
Here we present a design for flight insurance application.

#### Application setting

Suppose Alice wants to stand up a flight insurance service in the form of a smart contract `FlightInsurance`.
A user can buy a policy for her flight by sending money to the `FlightInsurance` Contract.
`FlightInsurance` offers a payout to the user should her insured flight be delayed or cancelled.
(Unfortunately, TC cannot detect whether you've been senselessly beaten and dragged off your flight by United Airlines.) 

#### Problem with the `Application` Contract

Similarly as the `Application` Contract, `FlightInsurance` Contract should also consist of those five basic components.
However, we don't want to query TC immediately after a user, say Bob, purchases a policy because if we do so, this will end up in two inappropriate cases.
One is that Bob purchases a policy for a flight that has already been delayed or cancelled, which is unfair to Alice.
The other is that Bob purchases a policy before the scheduled departure time of his flight so when the `FlightInsurance` Contract queries immediately, it will get response of not delayed since it has not even come to the time when the flight could be counted as delayed. This is unfair to Bob.

#### A scheme to get around the problem

To address this problem, we can separate two operations and deal with them at different times.
The `FlightInsurance` Contract need to include a `Insure()` function for a user to buy a policy for his flight a certain period ahead of the scheduled departure time, say 24 hours.
The contract can simply compare `block.timestamp` with the flight data to guarantee this restriction.
If the request is valid, then the contract will store the flight data and issue a policy ID to the user for querying TC later.
When the flight departs, the user can send a transaction to `Request()` with the policy ID in the `FlightInsurance` Contract, and the contract will query TC.
Then everything goes similarly to the procedure in the `Application` Contract.

This is a simple mechanism to design such a flight insurance contract.
You can look at [FlightInsurance.sol] for the complete `FligntInsurance` Contract logic.

[TownCrier.sol]: http://www.town-crier.org/code/TownCrier.sol
[Application.sol]: http://www.town-crier.org/code/Application.sol
[FlightInsurance.sol]: http://www.town-crier.org/code/FlightInsurance.sol
