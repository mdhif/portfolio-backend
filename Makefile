build:
	docker build -t portfolio-backend ./
start:
	docker run -p 8080:8080 -it --name portfolio-backend-container portfolio-backend
remove:
	docker rm portfolio-backend-container
	docker rmi portfolio-backend