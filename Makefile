VERSION=0.0.1

build:
	docker build -t spreadsheet2influx:$(VERSION) spreadsheet2influx

run:
	docker-compose -f docker-compose.yml up -d
