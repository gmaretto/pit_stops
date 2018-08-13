# Predicting Pit Stops in Formula 1

This repo contains code for obtaining and analyzing data about Formula 1 races from 2016 and 2017.

## Pit Stop Strategies

In most automotive competitions pitting during a race is necessary. The car may need fresh tyres, additional fuel, or more complex operations. 

In contemporary Formula 1, cars pit to change their tires. Teams have to devise a strategy, which involves several moving parts: the choice of tyres and other settings which influence tyre life, the ability to pass, achieve higher corner speed, etc

The strategy will also include an optimal pitting strategy:

1. How many time should we stop?
2. At which lap should we (ideally) stop?

Naturally, the answers to these questions may change during the race in response to exceptional events (weather, safety cars) and to the traffic conditions a driver faces during a race. 

Given available data, the focus will be on on-track conditions.

## Modeling Strategy
I have used the data in two forms. 

### 1. Race Level

At the level of a single race, to analyze and predict the number of pit stops *n(D,C,R)* for  driver *D* on a car *C*  in race *R*.

The first level of analysis is mostly used for descriptive purposes. Lacking any access to technical information (settings of tires, fuel,wings, brakes, power units), makes it very hard to obtain sharp predictions. 

Even with these limitations, a random forest was able to improve test error by a factor of 2, when compared to a naive prediction strategy (always predicting the mode of the traning set).

The output of this model can be used as a proxy for technical information in the Lap Level model

### 2. Lap Level
At the level of a single lap, to predict whether,in race *R*, driver *D* will pit in lap *L* or not: *p(D,C,R,L)*.

This model is intended as the basis of a tool to help team managers make their own pit stop decision during the race, by offering predictions of the pit stops of competitors.


## References
Libraries used in order of appearance:

#### *Beautiful Soup* for scraping files from the FIA website
https://www.crummy.com/software/BeautifulSoup/


#### *Tabula* and its Python wrapper _py-tabula_ for extracting data from PDF files
https://github.com/tabulapdf/
https://github.com/chezou/tabula-py

#### *Pandas* for cleaning and manipulating data
https://pandas.pydata.org/

#### _scikit-learn_ for using predictive and inferential models
http://scikit-learn.org/stable/


