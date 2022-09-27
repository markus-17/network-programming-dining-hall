# Network Programming - Laboratory Work Nr.1 - Dining Hall Component

## Table of contents
* [Description](#description)
* [Implementation](#implementation) 
* [How to run the project using Docker?](#how-to-run-the-project-using-docker)
* [What did I use?](#what-did-i-use) 

## Description

The purpose of this **Laboratory Work** was to create a restaurant simulation.

## Implementation

* If you are reading this version of the `README.md` file, then the implementation is ready for the `100% checkpoint`.
* The `Dining Hall` and the `Kitchen` components are web servers.
* The communication between these 2 components was configured.
* The implementation of `Dining Hall` logic is ready. That means multiple waiters are taking orders from multiple tables and then serve those orders back.

## How to run the project using Docker?

You may build each image separately and run the containers in the same Docker network, but I recommend using `docker compose`. For this, you will have to clone the `Kitchen` and `Dining Hall` repositories and at the same level create a file named `docker-compose.yaml` with the following contents:

```yaml
version: '3'
services:
  kitchen:
    container_name: kitchen
    build: network-programming-kitchen/
    ports:
      - 3000:3000
    environment:
      - USING_DOCKER_COMPOSE=1
  
  dining_hall:
    container_name: dining_hall
    build: network-programming-dining-hall
    ports:
      - 8080:8080
    depends_on:
      kitchen:
        condition: service_started
    environment:
      - USING_DOCKER_COMPOSE=1
```

Build the images using:

```
docker compose build
```

Run the containers using:

```
docker compose up
```


## What did I use?

* `Flask` and `requests` python libraries
* `Docker`
* `VS Code` editor