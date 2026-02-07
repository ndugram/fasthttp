from fasthttp import FastHTTP

app = FastHTTP(debug=True)


@app.post(url="https://httpbin.org/status/422", json={"invalid": "data"})
async def validation_error_test(resp):
    print("This won't be printed due to validation error")
    return resp.json()


if __name__ == "__main__":
    app.run()
