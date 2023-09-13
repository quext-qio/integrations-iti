# Create Documentation in local server

### Go to folder
```shell
cd src/documentation
```

### Set flask app to the file value
```shell
export FLASK_APP=app.py
```

### Set Environment
```shell
export FLASK_ENVIRONMENT=development
```


### Start server
```shell
python3 app.py
```

### Check if server is running in local
```shell
curl --location 'http://127.0.0.1:5000/'
```

### Open Swagger UI
```shell
open http://127.0.0.1:5000/swagger/#/
```

## Download Swagger
```shell
curl --location 'http://127.0.0.1:5000/download-swagger'
```