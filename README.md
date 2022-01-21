# mngt

Management Platform

## Run

```console
# Run the development serever
FLASK_APP=mngt.wsgi:app flask run

# Initialize the databse
FLASK_APP=mngt.wsgi:app flask init-db

# Seed the databse
FLASK_APP=mngt.wsgi:app flask seed-db

# Import the Excel file of COTS 2021
FLASK_APP=mngt.wsgi:app flask import-cots2021 ./path/to/excel/file
FLASK_APP=mngt.wsgi:app flask import-cots2021 ./mngt/tests/cots2021-proposals.xlsx
```


## Deployment

### Requirements

- Python 3.10
- Nginx

### Steps

Minimal Nginx configuration. This assumes that Cloudflare is providing certificate.

```plain
# /etc/nginx/sites-available/mngt
server {
    listen 80;
    server_name mngt.cots-conf.page;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
    }
}
```

Deployment steps.

```console
apt update

# web server
apt install nginx

# python and pyenv
sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

curl https://pyenv.run | bash
pyenv virtualenv 3.10.0 py3100

# clone the project and install python requirements
git clone https://github.com/cots-conf/mngt
cd mngt
pyenv local py3100
pip install -r requirements.txt

# install the service file
cp systemd/mngt.service /etc/systemd/system
systemctl daemon-reload
systemctl start mngt

# Create nginx configuration

# Restart/reload nginx
ln -s /etc/nginx/sites-available/mngt /etc/nginx/sites-enabled
```

```console
# initialize database
FLASK_APP=mngt.wsgi:app flask init-db

# seed or import data.
FLASK_APP=mngt.wsgi:app flask seed-db
FLASK_APP=mngt.wsgi:app flask import-cots2021 ./path/to/excel/file
```
