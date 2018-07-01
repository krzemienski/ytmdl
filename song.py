from colorama import init
from colorama import Fore, Style
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TRCK, TYER
from mutagen.mp3 import MP3
import requests
from defaults import DEFAULT
import itunespy
from print import PREPEND
import glob
import os

#----------------------cover--------------------

def dwCover(SONG_INFO, index):
    # Try to download the cover art as cover.jpg in temp
    try:
        imgURL = SONG_INFO[index].artwork_url_100
        try:
            # Try to get 512 cover art
            imgURL = imgURL.replace('100x100', '2048x2048')
        except:
            pass
        
        r = requests.get(imgURL)

        with open(DEFAULT.COVER_IMG, 'wb') as f:
            f.write(r.content)

        return True
    except TimeoutError:
        PREPEND(2)
        print('Could not get album cover. Are you connected to internet?\a')
        return False
    else:
        return False

#-----------------------tag----------------------

def getData(SONG_NAME):
    # Try to get the song data from itunes
    try:
        SONG_INFO = itunespy.search_track(SONG_NAME)
        return SONG_INFO
    except LookupError:
        PREPEND(2)
        print('Song not found!')
        return False
    except TimeoutError:
        PREPEND(2)
        print('Search timed out. Are you connected to internet?\a')
        return False
    else:
        PREPEND(2)
        print('Unknown Error!\a')
        return False

def getChoice(SONG_INFO, type):
    # Print 5 of the search results
    # In case less, print all

    PREPEND(1)
    print('Choose One')

    results = len(SONG_INFO)
    count = 0

    if results > 5:
        results = 5

    while count != results:
        print(Fore.LIGHTMAGENTA_EX,end='')
        print(' [' + str(count+1) + '] ',end='')
        print(Style.RESET_ALL,end='')
        print(Fore.LIGHTCYAN_EX,end='')
        if type == 'metadata':
            print(SONG_INFO[count].track_name,end='')
        if type == 'mp3':
            print(SONG_INFO[count]['title'],end='')
        print(Style.RESET_ALL,end='')
        print(' by ',end='')
        print(Fore.YELLOW,end='')
        if type == 'metadata':
            print(SONG_INFO[count].artist_name,end='')
        if type == 'mp3':
            print(SONG_INFO[count]['author_name'], end='')
        print(Style.RESET_ALL)

        count += 1

    while True:
        PREPEND(1)
        choice = input('Enter Choice [a valid choice] ')
        if choice <= str(results + 1) and choice > str(0):
            break

    choice = int(choice)
    choice -= 1
    return choice

def setData(SONG_INFO, is_quiet):
    # A variable to see if cover image was added.
    IS_IMG_ADDED = False

    try:
        # If more than one choice then call getChoice
        if len(SONG_INFO) > 1 and not is_quiet:
            option = getChoice(SONG_INFO, 'metadata')
        else:
            option = 0

        SONG_PATH = glob.glob(os.path.join(DEFAULT.SONG_TEMP_DIR,'*mp3'))

        audio = MP3(SONG_PATH[0], ID3=ID3)
        data = ID3(SONG_PATH[0])

        # Download the cover image, if failed, pass
        if dwCover(SONG_INFO, option):
            imagedata = open(DEFAULT.COVER_IMG, 'rb').read()

            data.add(APIC(3, 'image/jpeg', 3, 'Front cover', imagedata))

            # REmove the image
            os.remove(DEFAULT.COVER_IMG)

            IS_IMG_ADDED = True
        else:
            pass

        # If tags are not present then add them
        try:
            audio.add_tags()
        except:
            pass

        audio.save()

        option = int(option)

        data.add(TYER(encoding=3, text=SONG_INFO[option].release_date))
        data.add(TIT2(encoding=3, text=SONG_INFO[option].track_name))
        data.add(TPE1(encoding=3, text=SONG_INFO[option].artist_name))
        data.add(TALB(encoding=3, text=SONG_INFO[option].collection_name))
        data.add(TCON(encoding=3, text=SONG_INFO[option].primary_genre_name))
        data.add(TRCK(encoding=3, text=str(SONG_INFO[option].track_number)))

        data.save()

        DEFAULT.SONG_NAME_TO_SAVE = SONG_INFO[option].track_name + '.mp3'

        # Rename the downloaded file
        os.rename(SONG_PATH[0], os.path.join(DEFAULT.SONG_TEMP_DIR, DEFAULT.SONG_NAME_TO_SAVE))


        # Show the written stuff in a better format
        PREPEND(1)
        print('================================')
        print('  || YEAR: ' + SONG_INFO[option].release_date)
        print('  || TITLE: ' + SONG_INFO[option].track_name)
        print('  || ARITST: ' + SONG_INFO[option].artist_name)
        print('  || ALBUM: ' + SONG_INFO[option].collection_name)
        print('  || GENRE: ' + SONG_INFO[option].primary_genre_name)
        print('  || TRACK NO: ' + str(SONG_INFO[option].track_number))

        if IS_IMG_ADDED:
            print('  || ALBUM COVER ADDED')

        PREPEND(1)
        print('================================')

        return True
    except:
        return False