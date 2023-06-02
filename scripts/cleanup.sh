docker stop flask-app
docker rm flask-app
docker stop mypostgres
docker rm mypostgres
docker network rm mynetwork
docker rmi app