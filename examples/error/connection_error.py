from fasthttp import FastHTTP

app = FastHTTP(debug=True)


@app.get(url="https://random.domen.aiohttp/docs")
async def connection_test(resp):
    print("This won't be printed due to connection error")
    return resp.json()


if __name__ == "__main__":
    print("Testing connection error...")
    app.run()
