


utm_end_point을 아래와 같이 생성하고 명령어 실행해서 nginx 실행


```
#
# ❯ sudo vi /etc/nginx/sites-available/utm_end_point
# ❯ sudo nginx -t 
# ❯ sudo systemctl reload nginx
#

server {
  listen 30080;

  server_name better.cleanb.life; # Replace with your domain name
  auth_basic "Restricted Access";
  auth_basic_user_file /etc/nginx/.htpasswd;

  location / {
    proxy_pass http://localhost:2000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade'; 
    proxy_cache_bypass $http_upgrade;
    proxy_set_header X-Authenticated-User $remote_user;
  }

  location /api/ {
    proxy_pass http://localhost:3001; # Node.js 서버 포트로 프록시
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_set_header X-Authenticated-User $remote_user;
  }
}
```


node backend서버 실행.

```bash
npm init -y
npm install express cors
# create index.js
vi package.json
# "scripts": {
#    "start": "node index.js",
#    "test": "echo \"Error: no test specified\" && exit 1"
#  },
npm start
```

운영을 위해서 start.sh 생성