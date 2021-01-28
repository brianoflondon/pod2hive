

--------

# Pod2Hive - Podcast Censorship Protection 

## Experimental API to extract RSS from Hive

Use the following call:

```http://hive.noagendahost.com/hiverss/v1/rss/somethingtoreplacehere777```

[http://hive.noagendahost.com/hiverss/v1/rss/somethingtoreplacehere777](http://hive.noagendahost.com/hiverss/v1/rss/somethingtoreplacehere777)

You can also extract the same info as json:

```http://hive.noagendahost.com/hiverss/v1/json/somethingtoreplacehere777?pretty=true```

[http://hive.noagendahost.com/hiverss/v1/json/somethingtoreplacehere777?pretty=true](http://hive.noagendahost.com/hiverss/v1/json/somethingtoreplacehere777?pretty=true)

## More info

This Podcast is being automatically backed up to the Hive Blockchain. [You can find more information about this project here.](https://github.com/brianoflondon/pod2hive)


To Decode the RSS feed stored alongside this data, use the [rssfromhive.py](https://github.com/brianoflondon/pod2hive/blob/main/rssfromhive.py) script.

You can also fetch this data as a Json object direct from the Hive API with the following line:

```curl -s --data '{"jsonrpc":"2.0", "method":"database_api.find_accounts", "params": {"accounts":["somethingtoreplacehere777"]}, "id":1}' https://api.hive.blog```

The Json object returned will contain a ['pod-rss'] entry - this can be unpacked by running a bas64 decode followed by a zlib decompression. 
