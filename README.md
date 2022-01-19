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
