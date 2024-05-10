import jwt
import datetime

# Generate token
key = 'QIFqDewpalAyRThBl64IdNqM7WpFAJAL' # You get key from: curl -X GET http://localhost:8001/consumers/$CONSUMER/jwt  get key (ISS) of data[].key
private_key = open('private.pem', 'r').read()  # Load the private key
encoded_jwt = jwt.encode({'iss': f'{key}', 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=6000)},\
                          private_key, algorithm='RS256')
print(encoded_jwt)

