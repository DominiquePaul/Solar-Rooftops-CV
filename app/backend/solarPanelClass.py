import pandas as pd
import requests

import geopy
from geopy.geocoders import Nominatim

import numpy as np
import sys, os

class solarPanel:
    def __init__(self, address, area):
        # input parameters
        self._address = address
        self._area = area

        # fixed parameters
        self._year = 2010
        self._efficiency = 0.18 # standard Si solar panel
        self._pricePerWatt = 3.14 # in $/W for a conventional solar panel in standard condition at (1000 W/m^2) ref. https://news.energysage.com/how-much-does-the-average-solar-panel-installation-cost-in-the-u-s/
        self._lifeTime = 20 # years
        # self._pricePer_kWh = 0.15 # $/kWh ref. https://www.eia.gov/electricity/state/

        # derived parameters
        self._geolocator = Nominatim(user_agent="specify_your_app_name_here")
        self._location = self._geolocator.geocode(address)
        self._lat = self._location.latitude
        self._lon = self._location.longitude

        # calculated parameters
        self._pricePer_kWh = self.get_pricePer_kWh()  # $/kWh ref. https://www.eia.gov/electricity/state/
        self.meanLightIntensity = self.get_meanLightIntensity()
        self.elecPower = self.get_elecPower()
        self.investmentPrice = self.get_investmentPrice()
        self.monthlySaving = self.get_monthlySaving()

    @property
    def meanLightIntensity(self):
        return self.__meanLightIntensity

    @meanLightIntensity.setter
    def meanLightIntensity(self, value):
        self.__meanLightIntensity = value

    @property
    def elecPower(self):
        return self.__elecPower

    @elecPower.setter
    def elecPower(self, value):
        self.__elecPower = value
    
    @property
    def investmentPrice(self):
        return self.__investmentPrice
    
    @investmentPrice.setter
    def investmentPrice(self, value):
        self.__investmentPrice = value

    @property
    def monthlySaving(self):
        return self.__monthlySaving

    @monthlySaving.setter
    def monthlySaving(self, value):
        self.__monthlySaving = value

    def print_report(self):
        print("-----------------")
        print("meanLightIntensity = " + str(self.meanLightIntensity) + "W/m^2 (mean over 24h)")
        print("investmentPrice    = " + str(self.investmentPrice) + "$")
        print("elecPower          = " + str(self.elecPower) + "W (mean over 24h)")
        print("monthlySaving      = " + str(self.monthlySaving) + "$")

    def get_pricePer_kWh(self):
        # use a rough estimate
        return 0.13
        # actually calculate it
        attributes = 'zipcode='+str(self._location.address.split(',')[-2])
        url = 'https://us-zipcode.api.smartystreets.com/lookup?auth-id=cde64982-c946-f37d-ea45-6b9510262e46&auth-token=CW7KGE0HpdLdh0k4ajV8&' + attributes
        temp = requests.get(url).json()
        letter_code = str(temp[0]['city_states'][0]['state_abbreviation'])
        url = "http://api.eia.gov/series/?api_key=23d49b8c78010a9832aea1a47d102631&series_id=ELEC.PRICE." + letter_code + "-ALL.A"
        r = requests.get(url).json()
        return r['series'][0]['data'][0][1]/100.0

    def get_meanLightIntensity(self):
        attributes = 'ghi'  # ,dhi,dni,surface_air_temperature_nwp,solar_zenith_angle'
        interval = '60'  # or '30'
        api_key = '0cZ4RHQtbyTkdyjVfDvlcHi0nTVXmEXDzkQVC0ph'
        leap_year = 'false'
        your_name = 'Basile+Audergon'
        reason_for_use = 'beta+testing'
        your_affiliation = 'EPFL'
        your_email = 'basile.audergon@epfl.ch'
        mailing_list = 'false'
        utc = 'false'
        url = 'http://developer.nrel.gov/api/solar/nsrdb_0512_download.csv?wkt=POINT({lon}%20{lat})&names={year}&leap_day={leap}&interval={interval}&utc={utc}&full_name={name}&email={email}&affiliation={affiliation}&mailing_list={mailing_list}&reason={reason}&api_key={api}&attributes={attr}'.format(
            year=self._year, lat=self._lat, lon=self._lon, leap=leap_year, interval=interval, utc=utc, name=your_name, email=your_email,
            mailing_list=mailing_list, affiliation=your_affiliation, reason=reason_for_use, api=api_key,
            attr=attributes)
        df = pd.read_csv(url, skiprows=2)
        return df['GHI'].values.sum()/df.__len__()

    def get_elecPower(self):
        return self._area*self.meanLightIntensity*self._efficiency

    def get_investmentPrice(self):
        return self._pricePerWatt*self.elecPower

    def get_monthlySaving(self):
        return -self.investmentPrice/(12.0*self._lifeTime) + (self.elecPower*3600*24*30.4) * (self._pricePer_kWh/(1000*3600))# - investment + (Energy) * ($/Energie)

