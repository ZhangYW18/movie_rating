
To install packages
```shell
pip install -r requirements.txt 
```


To export packages
```shell
pipreqs .
```

Install mysqlclient on MacOS: see https://github.com/PyMySQL/mysqlclient
```shell
$ # Assume you are activating Python 3 venv
$ brew install mysql-client pkg-config
$ export PKG_CONFIG_PATH="$(brew --prefix)/opt/mysql-client/lib/pkgconfig"
$ pip install mysqlclient
```

