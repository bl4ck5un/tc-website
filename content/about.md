Title: What is Town Crier?
Date: 2017-4-6
slug: what-is-tc

For smart contracts on blockchain systems such as Ethereum, access to real-world data is critical.
A currency exchange contract must be able to learn current exchange rates.
A trip insurance contract must determine whether flights arrive on time.
A contract for the sale of a physical good needs to know whether the good was successfully delivered.
These are just a few of the many examples of applications that can only run with knowledge of real-world data or events.
A critical problem is: <i> Who can be trusted to provide data to smart contracts in a trustworthy way? </i>

The Town Crier (TC) system addresses this problem by using <i> trusted hardware </i>, namely the Intel SGX instruction set, a new capability in certain Intel CPUs.
TC obtains data from target websites specified in queries from application contracts.
TC uses SGX to achieve what we call its <i>authenticity property</i>.
<b> Assuming that you trust SGX, data delivered by TC from a website to an application contract is guaranteed to be free from tampering.</b>
This authenticity property means that to trust TC data, you only need to trust Intel's implementation of SGX and the target website.
You don't need to trust the operators of TC or anyone else.
Even the operators of the TC server cannot tamper with its operation or, for that matter, see the data it's processing. 

Thanks to its use of SGX and various innovations in its end-to-end design, Town Crier offers several properties that other oracles cannot achieve:
<ol>
  <li>Authenticity guarantee:</li>
  There's no need to trust any particular service provider(s) in order to trust Town Crier data.
  (You need only believe that SGX is properly implemented.) 
  <li>Succinct replies:</li>
  Town Crier can prune target website replies in a trustworthy way to provide short responses to queries.
  It does not need to relay verbose website responses.
  Such succintness is important in Ethereum, for instance, where message length determines transaction costs. 
  <li>Confidential queries:</li>
  Town Crier can handle <i> secret </i> query data in a trustworthy way.
  This feature makes TC far more powerful and flexible than conventional oracles.
</ol>

For more details on TC, its implementation using SGX, and its security guarantees, please read our paper [Town Crier: An Authenticated Data Feed for Smart Contracts].

TC can provide data in any ecosystem, but its first deployment is on Ethereum.

[Town Crier: An Authenticated Data Feed for Smart Contracts]: https://eprint.iacr.org/2016/168.pdf
