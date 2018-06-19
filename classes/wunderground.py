import argparse
from argparse import RawTextHelpFormatter
from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import quote
import configparser, sys, json, re, os, time
import ephem
import pytz
from singleton import Singleton
from settings import Settings
from logger import Logging


class LocationManager(Singleton):

    def __init__(self):
        try:
            if self.doneloading:
                pass
        except:
            self.name = "Wunderground"
            self.doneloading = True
            self.settings_c = Settings()
            self.logging = Logging()
            try:
                self.apikey = self.settings_c.get_setting("wunderground", "apikey")
                self.updateperiod = int(self.settings_c.get_setting("wunderground", "updateperiod"))
                self.language = self.settings_c.get_setting("wunderground", "language")
            except Exception as e:
                self.logging.error("Check your wunderground settings: " + str(e), location="wunderground")
            self.locations = {}

    def GetLocation(self, location, update = False):
        if not update:
            period = self.updateperiod
        else:
            period = update
        if location in self.locations.keys():
            return self.locations[location]
        else:
            self.locations[location] = ForecastData(self.apikey, location, update = period, language = self.language)
            return self.locations[location]

class ForecastData:

    data = None
    args = None
    verbose = False


    def __init__(self, api_key, location, update = 15, language = "EN", fetch = False):

        args = {}
        args["apikey"] = api_key
        args["location"] = location
        args["language"] = language
        args["fetch"] = -1
        args["sub"] = "fetch"

        self.args = args
        self.data_update = 0
        self.update_time = update*60
        
        self.logging = Logging()
        self.name = "Wunderground"

        if fetch:
            self.fetch_data()

    def check_update(self):
        if time.time()-self.update_time > self.data_update:
            self.fetch_data()
            
    def fetch_data(self):

        # Grab data from Weather Underground API
        req = ("http://api.wunderground.com/api/%s/conditions/alerts/forecast10day/lang:%s/q/%s.json"
               % (self.args["apikey"], self.args["language"], quote(self.args["location"])))
        self.link = req
        self.logging.info("Fetching weather data from location: " + str(self.args["location"]), location=self.name)

        try:
            response = urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason'):
                self.logging.error(e.reason, location=self.name)
            elif hasattr(e, 'code'):
                self.logging.error("Status returned: " + str(e.code), location=self.name)

        json_data = response.read().decode('utf-8', 'replace')
        data = json.loads(json_data)

        try:
            self.logging.error(data['response']['error']['description'], location=self.name)
            self.logging.error("Error fetching data, check settings", location=self.name)
        except KeyError:
            self.logging.info("Data fetched successfully", location=self.name)
            
            self.data = data
            self.data_update = time.time()


    def read_current(self):
        self.check_update()
        # Assign current conditions to a dictionary
        try:
            current = self.data['current_observation']
        except KeyError:
            self.fetch_error()

        # Collect and merge wind data
        wind_dir = current['wind_dir']
        wind_mph = current['wind_mph']
        wind_kph = current['wind_kph']
        wind_gust_mph = current['wind_gust_mph']
        wind_gust_kph = current['wind_gust_kph']
        wind_string_mph = (wind_dir + " " + str(float(wind_mph))
                        + "mph gusting to " + str(float(wind_gust_mph)) + "mph")
        wind_string_kph = (wind_dir + " " + str(float(wind_kph))
                        + "km/h gusting to " + str(float(wind_gust_kph)) + "km/h")
        wind = wind_dir + " " + str(float(wind_kph)) + "km/h"
        neerslag = current["precip_today_string"]
        neerslag = neerslag[neerslag.find("(")+1:neerslag.find(")")].replace(" ", "")
        
        current_dict = {
            "location"      : current["display_location"]["full"],
            "city"      : current["display_location"]["city"],
            "condition"    : current['weather'],
            "n_condition"	: self.get_numbered_state(self.convert_icon(current['icon'],True), True),
            "temp_f"       : int(round(float(current['temp_f']))),
            "temp_c"       : "%.1f" %(float(current['temp_c'])),
            "humidity"     : current['relative_humidity'].replace("%", ""),
            "icon"         : self.convert_icon(current['icon'],True),
            "icon_url"     : current['icon_url'],
            "wind"           : wind,
            "wind_dir"       : wind_dir,
            "wind_mph"       : wind_mph,
            "wind_kph"       : wind_kph,
            "wind_gust_mph"  : wind_gust_mph,
            "wind_gust_kph"  : wind_gust_kph,
            "wind_string_mph": wind_string_mph,
            "wind_string_kph": wind_string_kph,
            "pressure_mb"  : current['pressure_mb'],
            "pressure_in"  : current['pressure_in'],
            "pressure_trend" : current['pressure_trend'],
            "dewpoint_c"   : current['dewpoint_c'],
            "dewpoint_f"   : current['dewpoint_f'],
            "heat_index_c" : current['heat_index_c'],
            "heat_index_f" : current['heat_index_f'],
            "windchill_c"  : current['windchill_c'],
            "windchill_f"  : current['windchill_f'],
            "feelslike_c"  : current['feelslike_c'],
            "feelslike_f"  : current['feelslike_f'],
            "visibility_mi": current['visibility_mi'],
            "visibility_km": current['visibility_km'],
            "prec_hour_in" : current['precip_1hr_in'],
            "prec_hour_cm" : current['precip_1hr_metric'],
            "prec_day_mm"  : neerslag,
            "prec_day_cm"  : current['precip_today_metric'],
            "timezone"	   : current['local_tz_long'],
            "sunset"	   : self.get_next_sunset(current['local_tz_long'], current["display_location"]).strftime('%H:%M'),
            "sunrise"	   : self.get_next_sunrise(current['local_tz_long'], current["display_location"]).strftime('%H:%M'),
        }

        return current_dict


    def read_forecast(self):
        self.check_update()
        # Assign forecast to a dictionary
        forecast_dict = []

        try:
            forecast = self.data['forecast']['simpleforecast']['forecastday']
        except KeyError:
            self.fetch_error()

        count = 1

        for index, node in enumerate(forecast):

            d = node['date']
            if str(node['qpf_allday']['mm']) == "None":
                node['qpf_allday']['mm'] = "-"
                
            conditions = {
                "day"       : d['weekday'],
                "shortdate" : str(d['month']) + "/" + str(d['day']) + "/" + str(d['year']),
                "longdate"  : d['monthname'] + " " + str(d['day']) + ", " + str(d['year']),
                "low_f"     : node['low']['fahrenheit'],
                "low_c"     : node['low']['celsius'],
                "high_f"    : node['high']['fahrenheit'],
                "high_c"    : node['high']['celsius'],
                "avg_c"     : "%.0f" %((float(node['low']['celsius']) + float(node['high']['celsius'])) / 2.0),
                "avg_f"     : "%.0f" %((float(node['low']['fahrenheit']) + float(node['high']['fahrenheit'])) / 2.0),
                "icon"      : self.convert_icon(node['icon']),
                "icon_url"  : node['icon_url'],
                "condition" : node['conditions'],
                "n_condition"	: self.get_numbered_state(self.convert_icon(node['icon'])),
                "rain_in"   : node['qpf_allday']['in'],
                "rain_mm"   : str(node['qpf_allday']['mm']) + "mm",
                "snow_in"   : node['snow_allday']['in'],
                "snow_cm"   : str(node['snow_allday']['cm']) + "cm",
            }

            forecast_dict.append(conditions)
            count += 1

        return forecast_dict


    def read_info(self):
        self.check_update()
        try:
            info = self.data['current_observation']
        except KeyError:
            self.fetch_error()

        info_dict = {
            "city"        : info['display_location']['city'],
            "postal"      : info['display_location']['zip'],
            "datetime"    : info['observation_time'],
            "location"    : info['display_location']['full'],
            "country"     : info['display_location']['country'],
            "latitude"    : info['display_location']['latitude'],
            "longitude"   : info['display_location']['longitude'],
            "elevation"   : info['display_location']['elevation'],
            "observation" : info['observation_location']['full'],
        }

        return info_dict


    def read_alerts(self):
        self.check_update()
        alerts_dict = []

        try:
            alerts = self.data['alerts']
        except KeyError:
            self.fetch_error()

        for index, node in enumerate(alerts):

            a = {
                "start"       : node['date'],
                "expires"     : node['expires'],
                "description" : node['description'],
                "message"     : node['message'],
            }

            alerts_dict.append(a)

        return alerts_dict


    def convert_icon(self, icon, current=False):
        self.check_update()
        pattern = re.compile(r'[A-Za-z]+ \d+ (.+):\d+:\d+')
        time_string = self.data['current_observation']['local_time_rfc822']
        hour = int(pattern.search(time_string).group(1))
        day_icon_dict = self.get_icons_db()
        night_icon_dict = self.get_icons_db(day = False)
        try:
            if (hour > 20 or hour < 6) and current is True:
                new_icon = night_icon_dict[icon]
            else:
                new_icon = day_icon_dict[icon]
        except KeyError:
            self.logging.error("Icon type doesn't exist. Please report this. [%s]" %str(icon), location=self.name)
            new_icon = ""

        return new_icon
        
    def get_numbered_state(self, icon, current=False):
        day_icon_dict = self.get_icons_db()
        numbered_dict = self.get_icons_db(numbered=True)
        pattern = re.compile(r'[A-Za-z]+ \d+ (.+):\d+:\d+')
        time_string = self.data['current_observation']['local_time_rfc822']
        hour = int(pattern.search(time_string).group(1))
        if (hour > 20 or hour < 6) and current is True:
            add = 31
        else:
            add = 1
        for i in range(len(numbered_dict)):
            name = numbered_dict[i]
            if day_icon_dict[name][-1:] == icon[-1:]:
                return i + add
        return 20 + add

    def get_icons_db(self, day = True, numbered = False):
        if numbered:
             return [
                "chancerain",
                "sunny",
                "mostlysunny",
                "partlycloudy",
                "mostlycloudy",
                "rain",
                "chancesnow",
                "cloudy",
                "tstorms",
                "chancetstorms",
                "sleet",
                "snow",
                "fog",
                "smoke",
                "hazy",
                "flurries",
                "chanceflurries",
                "chancesleet",
                "clear",
                "partlysunny",
                "unknown"
            ]            
        elif day:
            return {
                "chancerain"    : "weather_g",
                "sunny"         : "weather_h",
                "mostlysunny"   : "weather_b",
                "partlycloudy"  : "weather_c",
                "mostlycloudy"  : "weather_d",
                "rain"          : "weather_i",
                "chancesnow"    : "weather_u",
                "cloudy"        : "weather_e",
                "tstorms"       : "weather_m",
                "chancetstorms" : "weather_k",
                "sleet"         : "weather_j",
                "snow"          : "weather_q",
                "fog"           : "weather_f",
                "smoke"         : "weather_n",
                "hazy"          : "weather_t",
                "flurries"      : "weather_p",
                "chanceflurries": "weather_s",
                "chancesleet"   : "weather_o",
                "clear"         : "weather_r",
                "partlysunny"   : "weather_l",
                "unknown"       : "weather_u"
            }
        else:
            return {
                "chancerain"    : "weather_nt_g",
                "sunny"         : "weather_nt_a",
                "mostlysunny"   : "weather_nt_b",
                "partlycloudy"  : "weather_nt_c",
                "mostlycloudy"  : "weather_nt_d",
                "rain"          : "weather_nt_i",
                "chancesnow"    : "weather_nt_u",
                "cloudy"        : "weather_nt_e",
                "tstorms"       : "weather_nt_m",
                "chancetstorms" : "weather_nt_k",
                "sleet"         : "weather_nt_j",
                "snow"          : "weather_nt_q",
                "fog"           : "weather_nt_f",
                "smoke"         : "weather_nt_n",
                "hazy"          : "weather_nt_t",
                "flurries"      : "weather_nt_p",
                "chanceflurries": "weather_nt_s",
                "chancesleet"   : "weather_nt_o",
                "clear"         : "weather_nt_r",
                "partlysunny"   : "weather_nt_l",
                "unknown"       : "weather_nt_u"
            }

    def getCondNames(self, language = "EN"):
        if language == "EN":
            return [
                "chancerain",
                "sunny",
                "mostlysunny",
                "partlycloudy",
                "mostlycloudy",
                "rain",
                "chancesnow",
                "cloudy",
                "tstorms",
                "chancetstorms",
                "sleet",
                "snow",
                "fog",
                "smoke",
                "hazy",
                "flurries",
                "chanceflurries",
                "chancesleet",
                "clear",
                "partlysunny",
                "unknown"
            ]

    def fetch_error(self):
        pass

    def output_data(self, parser):

        if self.args.sub == "current":
            current_dict = self.read_current()
            print(current_dict[self.args.current], file=sys.stdout)
        elif self.args.sub == "forecast":
            forecast_dict = self.read_forecast()
            self.logging.info(forecast_dict[int(self.args.day)][self.args.forecast], location=self.name)
        elif self.args.sub == "info":
            info_dict = self.read_info()
            print(info_dict[self.args.information], file=sys.stdout)
        elif self.args.sub == "alert":
            alerts_dict = self.read_alerts()

            if len(alerts_dict) < 1:
                print('No alerts to display')
                sys.exit(10)

            if self.args.num > len(alerts_dict):
                self.logging.error('Invalid alert number. Available: %s' % len(alerts_dict), location=self.name)

            print(alerts_dict[int(self.args.num-1)][self.args.alert], file=sys.stdout)
        elif self.args.sub != "fetch":
            parser.print_usage()


    def get_next_sunrise(self, timezone, location):
        tz = pytz.timezone(timezone)
        obs = self.create_observer(location)
        sunrise = obs.next_rising(ephem.Sun()).datetime()
        return pytz.utc.localize(sunrise).astimezone(tz)

    def get_next_sunset(self, timezone, location):
        tz = pytz.timezone(timezone)
        obs = self.create_observer(location)
        sunset = obs.next_setting(ephem.Sun()).datetime()
        return pytz.utc.localize(sunset).astimezone(tz)
        
    def create_observer(self, loc):
        user = ephem.Observer()
        #print(loc)
        user.lat = loc["latitude"]
        user.lon = loc["longitude"]
        user.elevation = float(loc["elevation"])
        return user
