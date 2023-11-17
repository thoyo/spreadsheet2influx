VERSION=0.0.1

build_spreadsheet2influx:
	docker build -t spreadsheet2influx:$(VERSION) spreadsheet2influx

build_all:
	docker build -t spreadsheet2influx:$(VERSION) spreadsheet2influx
	docker build -t simulator:$(VERSION) simulator

run_spreadsheet2influx:
	docker-compose -f docker-compose.yml up -d

run_all:
	docker-compose -f docker-compose.yml -f docker-compose.simulator.yml up -d
