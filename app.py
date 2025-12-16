from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def hello():
    # Artificial CPU load
    start = time.time()
    while time.time() - start < 0.2:
        pass
    return "DevOps App is running with autoscaling 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
