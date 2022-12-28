# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# This script is part of our solar monitoring project. See:
# https://github.com/greiginsydney/Get-PowerWallData.py
# https://greiginsydney.com/get-powerwalldata-py
# https://greiginsydney.com/category/prtg/


# from *WINDOWS* call as: python ./Get-PowerWallData.py '{\"host\":\"powerwall\"}'
# Get-PowerWallData\python> &"C:\Program Files (x86)\PRTG Network Monitor\python\python" ./Get-PowerWallData.py '{\"host\":\"powerwall\"}'


import pypowerwall  # Thank you Jason! https://github.com/jasonacox/pypowerwall
import json
import re           # for the regex replacement (sub)
import sys

# Optional: Turn on Debug Mode
# pypowerwall.set_debug(True)

# Credentials for your Powerwall - Customer Login Data
password='ABCD1234'
email='example@example.com'
timezone = "Australia/Sydney"  # Your local timezone. Reference: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

#Adjust this figure for your local market. This is used to calculate the Battery Health value
batteryNew = 13200 #Tesla warrants the battery as 13.2kWh in AU, as at 9 Feb 2017. See https://www.tesla.com/sites/default/files/pdfs/powerwall/Powerwall_2_AC_Warranty_AUS-NZ_1-0.pdf


try:
    host = ''
    if len(sys.argv) > 1:
        args = json.loads(sys.argv[1])
        # Check for 'host' and 'params' keys in the passed JSON, with params taking precedence:
        # (We strip any http or https prefix, but there's no other validation)
        for i in ("host", "params"):
            if args.get(i):
                host = re.sub("https?:", "", args[i]).strip().strip('/')
    if len(host) == 0:
        result = {'prtg': {'text' : 'Unsufficient or bad arguments', 'error' : {'args' : sys.argv}}}
        print(json.dumps(result))
        sys.exit(1)
    else:
        result = {'prtg': {'text' : "This sensor queries %s" % host}}

    # Connect to Powerwall
    pw = pypowerwall.Powerwall(host,password,email,timezone)
    if not pw.is_connected():
        result = {'prtg': {'text' : 'Unable to connect to {}'.format(host)}}
        print(json.dumps(result))
        sys.exit(1)

    result['prtg'].update({'result': []})

    result['prtg']['result'].append(
        {'Channel' : 'Battery charge',
        'Value' : "{:.0f}".format(pw.level()),
        'Unit' : 'Percent',
        'Float' : 0,
        'ShowChart' : 1,
        'ShowTable' : 1,
        'Primary' : 1
        })

    result['prtg']['result'].append(
        {'Channel' : 'Grid',
        'Value' : "{:.3f}".format(pw.grid()/1000),
        'Unit' : 'Custom',
        'CustomUnit' : 'kW',
        'Float' : 1,
        'ShowChart' : 1,
        'ShowTable' : 1,
        })

    result['prtg']['result'].append(
        {'Channel' : 'Battery',
        'Value' : "{:.3f}".format(pw.battery()/1000),
        'Unit' : 'Custom',
        'CustomUnit' : 'kW',
        'Float' : 1,
        'ShowChart' : 1,
        'ShowTable' : 1
        })

    result['prtg']['result'].append(
        {'Channel' : 'Home',
        'Value' : "{:.3f}".format(pw.load()/1000),
        'Unit' : 'Custom',
        'CustomUnit' : 'kW',
        'Float' : 1,
        'ShowChart' : 1,
        'ShowTable' : 1
        })

    result['prtg']['result'].append(
        {'Channel' : 'Solar',
        'Value' : "{:.3f}".format(pw.solar()/1000),
        'Unit' : 'Custom',
        'CustomUnit' : 'kW',
        'Float' : 1,
        'ShowChart' : 1,
        'ShowTable' : 1
        })

    temps = pw.temps()
    whichBattery = 1
    for thisBattery in temps:
        if len(temps) == 1:
            batteryLabel = 'Battery temperature'
        else:
            batteryLabel = "Battery {} temperature".format(whichBattery)
        result['prtg']['result'].append(
            {'Channel' : batteryLabel,
            'Value' : "{:.01f}".format(temps[thisBattery]),
            'Unit' : 'Temperature',
            'Float' : 1,
            'ShowChart' : 1,
            'ShowTable' : 1
            })
        whichBattery += 1

    batteryStatus = pw.system_status()['battery_blocks']
    whichBattery = 1
    for thisBattery in batteryStatus:
        if len(temps) == 1:
            batteryLabel = 'Battery health'
        else:
            batteryLabel = "Battery {} health".format(whichBattery)
        batteryFull = thisBattery['nominal_full_pack_energy']
        result['prtg']['result'].append(
            {'Channel' : batteryLabel,
            'Value' : "{:.0f}".format((batteryFull / batteryNew) * 100),
            'Unit' : 'Percent',
            'Float' : 1,
            'ShowChart' : 0,
            'ShowTable' : 1
            })
        whichBattery += 1

    result['prtg']['result'].append(
        {'Channel' : 'PowerWall version',
        'Value' : "{}".format(pw.version()[0]),
        'Unit' : 'Custom',
        'CustomUnit' : '&nbsp;',
        'Float' : 0,
        'ShowChart' : 0,
        'ShowTable' : 1,
        'ShowChanged' : 1
        })

except Exception as e:
    result = {'prtg': {'text' : 'Python Script execution error', 'error' : "%s" % str(e)}}

print('')
print(json.dumps(result))
print('')

# References:
# pypowerwall https://github.com/jasonacox/pypowerwall
# Tesla Powerwall 2 - Local Gateway API documentation https://github.com/vloschiavo/powerwall2
