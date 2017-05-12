Title: FAQ
Date: 2017-4-6

## What is Town Crier (TC)?

TC is an authenticated data feed for smart contracts, a.k.a. an "oracle." It was created by students and faculty at The Initiative for CryptoCurrencies and Contracts (IC3), the world’s leading academic research initiative in blockchains.

TC isn’t like other existing “oracles,” though. Thanks to its use of SGX, TC provides unusually strong authentication for data and can also provide strong confidentiality for smart contract queries and operations. (See below.)

## Do I have to trust a ragtag bunch of students and professors in order to trust TC?

No! TC runs in a secure enclave, a trusted execution environment protected by a powerful new Intel technology called SGX. SGX prevents _even the owners of the host on which TC is running, i.e., us, from altering TC’s execution or seeing the data it processes_.

Of course, you need to trust that Intel has implemented SGX correctly, and the research community has already identified some caveats around SGX confidentiality (side-channel attacks). We do not believe they are applicable to TC’s current cryptographic algorithms or set of query types.

You do of course have to trust that TC has been correctly implemented, which is one reason why we make the source code publicly available.

## Is TC using a full production version of SGX?

Yes.

## Don’t I have to trust Intel to ensure the integrity and confidentiality of my data?

No, you don’t. Intel cannot exfiltrate data from a secure enclave. Additionally, it would be hard for Intel to clone the TC service. They would have to generate their own TC public key, something easily detectable.

Of course, we say this under the assumption that Intel doesn’t have backdoors we don’t know about. If they do, though, you probably need to worry about using an Intel CPU to begin with. (Yes, that little thing on the motherboard in your laptop…)

## Do I have to trust the website from which data is being sourced by TC?

Yes. TC cannot fix corrupted data sources… yet. In a future version, TC will combine data from multiple sources, allowing for correction of corruption of some of them.

## How mature is your current version of TC?

We regard the current version as an alpha deployment. We’re still working on a bunch of new query types, security features, developer tools, and so forth.

## Can TC be used on blockchains other than the public Ethereum blockchain?

Yes. It can be used in permissioned blockchains, for instance. Even in cases where trusted data sources are available, its confidentiality features can be useful for running portions of smart contracts in a private way. We are working to various companies and platform creators to adapt TC for a variety of deployment settings.

## Is Town Crier free?

The Ethereum service is free. And we plan to expand it to meet the evolving needs of the Ethereum community. TC is patent-pending, however, and we encourage you to seek a license for commercial uses.

## How can I learn more?

See our Research page.

## Are you working with outside developers on TC?

We’re continuing to develop TC and are working with commercial partners to do so. If you’re interested in working with us, however, we’re happy to hear from you.

## What other cool projects are coming out of IC3?

We encourage you to explore soon-to-be-deployed projects like Teechain (which also uses SGX), Honeybadger, and Solidus. Visit IC3 at [www.initc3.org](www.initc3.org) or [ic3.cornell.edu](ic3.cornell.edu).
