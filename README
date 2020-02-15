# Installing required components and general set up

This project requires that docker, python3.8 >=, pip, make and curl be pre-installed
Install those, then run 'make install'. Then run the command `export FLASK_APP=src/app.py`.

This tells the flask command where the application to run is located. Also be sure to obtain a .env file
from a project maintainer that has one, and place it in the src directory.

# Running Backend

To run backend, you first need to build the "base" docker image which includes all of the python dependencies our server
uses. To do this, in the backend repository folder run `make install` and `make build-base` OR run `make install` from the
top level chefmoji folder. Then, you can run the following commands:
`make prod`: run app in pseudo-production mode. Navigate to localhost:8080 to play with the application.
`make debug-prod`: spawn an sh shell in the created docker instance that normally simply runs in production. Useful
for debugging purposes.

Notes on Protocol Buffers:
.proto and compiled .py files are located under src/protocol_buffers

