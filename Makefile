IMAGE_NAME := "coins-telethon:latest"

build:
		docker build -t ${IMAGE_NAME} .

up:
		docker run --env-file=.env --rm -p5000:5000 -v"$(CURDIR)":/app ${IMAGE_NAME}
