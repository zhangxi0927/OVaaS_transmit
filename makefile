build:
	docker build --tag ovaas/func-humanpose:v1.0.0 .
run:
	docker run -p 8080:80 -it --rm ovaas/func-humanpose:v1.0.0