# Installation Guide

## Data Collection

Indicate how to collect the data necessary for this project :
- Where and how to get the data ?
- Where and how to integrate the data in the repository ? (example : in the direcctory data/raw)

## Dependencies

* This project is developed with Python as the core programming language and utilizes Streamlit for designing, building, managing data and web interface.

# Application Dependencies
* List of Python dependencies:
  * streamlit
  * numpy
  * pandas
  * joblib
  * matplotlib
  * requests
  * geopandas
  * openpyxl

## Development

# Prerequisites
# Install Docker on the machine running the application (follow the instructions at https://docs.docker.com/engine/install/)

# Installation Steps
1. Clone this project.
2. Run the Dockerfile using the following command:
   docker run -d -p 8080:8080 --rm datalela-apps
3. Access the application at "http://localhost:8080"

## Production

Indicate, if it exist, a documentation to run the solution in production mode.
