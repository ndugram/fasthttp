from fasthttp import FastHTTP

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/delay/10")
async def timeout_request(resp):
    print("This won't be printed due to timeout")
    return resp.json()


if __name__ == "__main__":
    app.run()
