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
        {'channel' : 'Battery charge',
        'value' : "{:.0f}".format(pw.level()),
        'unit' : 'Custom',
        'float' : 0,
        'showChart' : 1,
        'showTable' : 1,
        'primary' : 1
        })

    result['prtg']['result'].append(
        {'channel' : 'Grid',
        'value' : "{:.3f}".format(pw.grid()/1000),
        'unit' : 'Custom',
        'customUnit' : 'kW',
        'float' : 1,
        'showChart' : 1,
        'showTable' : 1,

        })

    result['prtg']['result'].append(
        {'Channel' : 'Battery',
        'value' : "{:.3f}".format(pw.battery()/1000),
        'unit' : 'Custom',
        'customUnit' : 'kW',
        'float' : 1,
        'showChart' : 1,
        'showTable' : 1
        })

    result['prtg']['result'].append(
        {'Channel' : 'Load',
        'value' : "{:.3f}".format(pw.load()/1000),
        'unit' : 'Custom',
        'customUnit' : 'kW',
        'float' : 1,
        'showChart' : 1,
        'showTable' : 1
        })

    result['prtg']['result'].append(
        {'Channel' : 'Solar',
        'value' : "{:.3f}".format(pw.solar()/1000),
        'unit' : 'Custom',
        'customUnit' : 'kW',
        'float' : 1,
        'showChart' : 1,
        'showTable' : 1
        })

except Exception as e:
    result = {'prtg': {'text' : 'Python Script execution error', 'error' : "%s" % str(e)}}

print('')
print(json.dumps(result))
print('')

# References:
# pypowerwall https://github.com/jasonacox/pypowerwall
# Tesla Powerwall 2 - Local Gateway API documentation https://github.com/vloschiavo/powerwall2
