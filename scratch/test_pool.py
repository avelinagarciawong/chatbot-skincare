import asyncio
from twscrape import API

async def main():
    api = API()
    # Search for tweets containing links (using "filter:links" or looking for tweets where links list is not empty)
    count = 0
    async for tweet in api.search("skincare filter:links lang:id", limit=50):
        if tweet.links:
            print(f"Tweet ID: {tweet.id}")
            print(f"Content: {tweet.rawContent}")
            print(f"Links ({type(tweet.links)}): {tweet.links}")
            for link in tweet.links:
                print(f"  - Link item type: {type(link)}, value: {link}")
            count += 1
            if count >= 3:
                break

if __name__ == "__main__":
    asyncio.run(main())
