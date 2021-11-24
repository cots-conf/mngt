import os

from mngt import create_app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("WEBAPP_HOST", "127.0.0.1")
    port = int(os.getenv("WEBAPP_HOST", "5000"))
    app.run(host=host, port=port)
