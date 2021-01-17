# pod2hive

It'll be great one day.

Proof of concept... done.

First step: I want to turn Hive into the most amazing place to backup a podcast. 

This is my hacky minimal code to pull an RSS feed from a Hive User's account.

So far the only account with data in it is called learn-to-code

https://github.com/brianoflondon/pod2hive/blob/main/rssfromhive.py

The only thing you'll need is

```pip install beem```

If you want to see the raw data on the blockchain you can look at it here. You'll see it on the left with "Posting json metadata"

https://hiveblocks.com/@learn-to-code

You can get a json version direct from the web:

https://hive.blog/@learn-to-code.json

To Decode this to RSS you can use the code here:

This site is a rudimentary API server that pulls out the RSS from any Hive account which has one:

http:/hive.noagendahost.com/hiverss/v1/rss/learn-to-code

https://github.com/brianoflondon/pod2hive/blob/main/rssfromhive.py

If you're eyes are working, you'll find the PodcastIndex data for my podcast is then followed by a compressed and character encoded (but not cryptographically encoded) block of data that is the RSS feed.

This is the exact transaction on the blockchain which I put in:

https://hiveblocks.com/tx/e83916d2be6e4d87dddab83ca90b8ae17422fb40

The code that writes to the blockchain is:

https://github.com/brianoflondon/pod2hive/blob/main/hiveforpod.py

This code relys on me having entered private posting keys for the "learn-to-code" hive account into something called "beempy" which is a command line interface to store keys on my machine. Only with that on my machine can I post to the blockchain but that is all I require.

You don't need keys or an account to read public data from the chain. I belive there is a simple curl way of accessing this data but I need to do some work on that becuase of the encoding.

This will extract the RSS data from the Chain as well as PodcastIndex's data about the podcast.

```curl -s --data '{"jsonrpc":"2.0", "method":"database_api.find_accounts", "params": {"accounts":["no-agenda"]}, "id":1}' https://api.hive.blog```

The RSS feed is encoded with base64 and zlib compression.

Loads of work needed but I'm on my way.


# Payments to Podcasts

We want to stream small payments to podcast creators and others involved in the value chain of podcasting.

First
