## Getting started
This if from this repo: 
https://github.com/Kong/docker-kong/tree/master/compose

It all works in docker-compose.
I've changed a little bit docker-compose.yml coming from kong repo, by adding my to-do application, and some SSL certs (needed for Oauth plugin)
- Oauth2.0 plugin works only in SSL mode so instead of 8000 port we must use https which is on 8443
But this is not default - use additional config in docker
https://github.com/Kong/kong/issues/4181

## Upstream
You can manually add upstream to todo-app.
Check IP address of todo app, for upstream service configuration.
```
docker inspect compose_todo-app_1
```
## JWT, Oauth2.0

#### Run docker-compose
```
openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout certificate.key -out certificate.crt
make kong-postgres
export CONSUMER=rafal
```

#### Get consumers
export CONSUMER=rafal
curl -X GET http://localhost:8001/consumers/$CONSUMER/jwt


http://localhost:8000/beta?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIzMzMifQ.jd0tXQrBQHlD63tyCIaUZvk7u7ijFGKcUDIfk53eFSs

#### List plugins:
curl http://localhost:8001/plugins/ | jq



#### This adds verification for both nbf and exp claims:
```
curl http://localhost:8001/plugins/f4be975c-1b54-4962-8695-4c3423a49e99 | jq
 
curl -X PATCH http://localhost:8001/plugins/f4be975c-1b54-4962-8695-4c3423a49e99 \
 --data "config.claims_to_verify=exp"

curl http://localhost:8001/plugins/f4be975c-1b54-4962-8695-4c3423a49e99 | jq
```
#### Create key pair for signing JWT token (singatures)

openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -outform PEM -pubout -out public.pem

#### Create JWT token.
```
curl -X POST http://localhost:8001/consumers/$CONSUMER/jwt \
 -F "rsa_public_key=@./public.pem" 
```
#### Sign JWT token with private key using my custom python script
```
python3 sign_jwt_with_private_key.py
```

### Oauth
That means, that some feature of Kong, e.g. Oauth, needs SSL, HTTPS, so we need generate cert
openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout certificate.key -out certificate.crt
and add some env in docker compose for kong app.

1. Turn on Oauth plugin (service or gloabally)
2. Create Oauth client in specific consumer to get client id and client secret
3. Get access code or token depending on the chosen flow

curl -sX GET http://localhost:8001/oauth2_tokens/

basic auth   cmFmYWw6MzMzCg==
```
echo rafal:123456 | base64

curl http://localhost:8000/beta --header "Authorization: Basic cmFmYWw6MTIzNDU2Cg=="
```

#### Generate SSL cert

openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout certificate.key -out certificate.crt


#### Client credentials - client_crendential flow:
```
curl --request POST -k \
 --url 'https://127.0.0.1:8443/todo-gservices/oauth2/token' \
 --data "client_id=1234" \
 --data "client_secret=12345" \
 --data "grant_type=client_credentials"
```

### Troubleshooting:
```
curl --request POST -k  --url 'https://127.0.0.1:8443/todo-gservices/oauth2/token'  --data "client_id=1234"  --data "client_secret=12345"  --data "grant_type=client_credentials"
curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to 127.0.0.1:8443 
```
That means, that some feature of Kong, e.g. Oauth, needs SSL, HTTPS, so we need generate cert
openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout certificate.key -out certificate.crt
and add some env
Solution:
In docker compose you must add a such fields:
      # ssl config
      KONG_PROXY_LISTEN: 0.0.0.0:8000, 0.0.0.0:8443 ssl
      KONG_ADMIN_LISTEN: 0.0.0.0:8001, 0.0.0.0:8444 ssl
      KONG_SSL_CERT: /etc/ssl/certs/certificate.crt
      KONG_SSL_CERT_KEY: /etc/ssl/certs/certificate.key
      KONG_ADMIN_SSL_CERT: /etc/ssl/certs/certificate.crt
      KONG_ADMIN_SSL_CERT_KEY: /etc/ssl/certs/certificate.key

and a such volumes:
    volumes:
      - type: bind
        source: /home/rafal/gitlab-project/public-projects/kong-examples/docker-kong/compose/certificate.key
        target: /etc/ssl/certs/certificate.key
      - type: bind
        source: /home/rafal/gitlab-project/public-projects/kong-examples/docker-kong/compose/certificate.crt
        target: /etc/ssl/certs/certificate.crt