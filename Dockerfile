# We create our base from the official Python3 image 
FROM python:3
#We copy our bot script and our config file to the image
COPY ./traderBot.py .
COPY ./config.json .
# We install the required dependencies
RUN pip3 install requests yfinance pycron
# We run our script
CMD [ "python", "-u", "./traderBot.py" ]