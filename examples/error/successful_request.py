from fasthttp import FastHTTP

app = FastHTTP(debug=True)


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def successful_request(resp):
    print(f"✓ Success! Status: {resp.status}")
    print(f"Response: {resp.json()}")
    return resp.json()


if __name__ == "__main__":
    print("Testing successful request...")
    app.run()
