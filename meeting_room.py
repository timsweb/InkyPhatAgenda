from __future__ import print_function
import httplib2
import os
import time
import calendar
import icalendar
import datetime
from dateutil.parser import *
from dateutil.tz import tzlocal
from PIL import Image, ImageFont
import inkyphat
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try: 
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'MeetingRoomDisplay'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-meetingroom.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 3 events')
    eventsResult = service.events().list(
        calendarId='wordery.com_3730353932343637343331@resource.calendar.google.com', timeMin=now, maxResults=3, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    #inkyphat.set_border(inkyphat.BLACK)
    inkyphat.set_rotation(180)
     
    inkyphat.rectangle((0, 0, inkyphat.WIDTH, inkyphat.HEIGHT), fill=inkyphat.WHITE)
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 14)
    fontBold = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 14)
    fontBoldBig = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 15)
    offset_x, offset_y = 5, 0
    hasCurEvent = False
    if not events:
        print('No upcoming events found.')
        text = "No upcoming events found."
        inkyphat.text((offset_x, offset_y), text, inkyphat.RED, font=font)
    for event in events:
        start = parse(event['start'].get('dateTime', event['start'].get('date')))
        end = parse(event['end'].get('dateTime', event['end'].get('date')))
        print(start, end, event['summary'])
        colour = inkyphat.BLACK
        prefix = 'Next '
        if start < datetime.datetime.now(tzlocal()) and end > datetime.datetime.now(tzlocal()):
            hasCurEvent = True
            colour = inkyphat.RED
        #text = "{} - {}: {}".format(start.strftime('%a %H:%M'), end.strftime('%H:%M'), event['summary'])
        text = "{} - {}:".format(start.strftime('%a %H:%M'), end.strftime('%H:%M'))
        inkyphat.text((offset_x, offset_y), text, colour, font=fontBold)
        offset_y += fontBold.getsize(text)[1] + 2
        text = event['summary']
        inkyphat.text((offset_x + 10, offset_y), text, colour, font=font)
        offset_y += font.getsize(text)[1] + 2
        if offset_y >= inkyphat.HEIGHT:
            break
    curTime = datetime.datetime.now(tzlocal()).strftime('%H:%M')
    timeOffset = fontBoldBig.getsize(curTime)
    timeBox = [inkyphat.WIDTH - timeOffset[0] - 8, inkyphat.HEIGHT - timeOffset[1], inkyphat.WIDTH, inkyphat.HEIGHT]
    inkyphat.rectangle(timeBox, fill=inkyphat.RED if hasCurEvent else inkyphat.BLACK)
    inkyphat.text((inkyphat.WIDTH - timeOffset[0] - 6, inkyphat.HEIGHT - timeOffset[1]), curTime, inkyphat.WHITE, font=fontBoldBig)
    inkyphat.show()

if __name__ == '__main__':
    main()
