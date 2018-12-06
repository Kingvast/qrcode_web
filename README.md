# qrcode_web
App介绍，下载。使用二维码扫码后下载

### 安装步骤
1. 安装docker
2. 在项目根目录执行 ./start_develop

### 进入 docker 容器
```
python manage.py sync_db
python manage.py runserver
```

### 创建 couchdb 的管理员
有两种方式：

1. curl -s -X PUT http://couchdb:5984/_node/nonode@nohost/_config/admins/develop -d '"devpwd"'
2. 使用管理界面： http://<docker machine ip>:5984/_utils/#addAdmin/nonode@nohost
