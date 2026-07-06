import asyncio
from twscrape import API, gather

async def test_query(api, query, limit=30):
    print(f"\nTesting query: '{query}'")
    try:
        tweets = await gather(api.search(query, limit=limit))
        print(f"Retrieved: {len(tweets)} tweets")
        if tweets:
            for i, tw in enumerate(tweets[:3]):
                print(f"  [{i}] ID: {tw.id} | Date: {tw.date} | User: {tw.user.username}")
                clean_text = tw.rawContent.encode('ascii', 'ignore').decode('ascii')
                print(f"      Text: {clean_text[:80]}...")
        return len(tweets)
    except Exception as e:
        print(f"  Error: {e}")
        return 0

async def main():
    api = API()
    await test_query(api, "review skincare", limit=10)
    await test_query(api, "skincare bagus", limit=10)
    await test_query(api, "Somethinc", limit=10)
    await test_query(api, "Skintific", limit=10)

if __name__ == "__main__":
    asyncio.run(main())
