from fastapi import FastAPI, HTTPException

app = FastAPI()

# Route để lấy phiên bản ứng dụng
@app.get("/get_version")
def get_version():
    return {"version": "1.0.0"}

# Route để kiểm tra số nguyên tố
@app.post("/check_prime")
def check_prime(number: int):
    if number < 2:
        raise HTTPException(status_code=400, detail="Number must be >= 2")
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return {"number": number, "is_prime": False}
    return {"number": number, "is_prime": True}
