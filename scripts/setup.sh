# Pull requirements
docker pull postgres
docker build --no-cache -t app:latest ../
docker network create mynetwork
docker run --name mypostgres -e POSTGRES_PASSWORD=1234 --network mynetwork -d postgres
docker run --name flask-app -p 5000:5000 --network=mynetwork -d app