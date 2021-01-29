"""
This program is my attempt at making a basic bms file player (a rhythm game) in python with pygame. The
implementation of the format is only partial, many songs won't work correctly and crashes may occur as well sometimes
but you can still have fun with it.
A BMS song consists of a folder full of short sound files and a BMS file that coordinates them into a playable song.
You will need to download some songs to play this game. BMS is always free but I don't have the rights to redistribute
so I won't give you any by default, sorry.
After the first launch, the game will create a database of songs, db.pkl. If you want to add new songs, press F5 in the
game to rebuild it.
The game will also save scores in the root directory, in scoredb.pkl. Even if you refresh the song database, the score
database will still work so don't worry, it's safe.

"""

import pygame
import sys
import re
import time
import os
import pickle
import hashlib
from pygame.locals import *

RED = (255, 0, 0)
PURPLE = (255, 0, 255)
BLUE = (0, 255, 255)
WHITE_NUMBER = 900  # The portion of the screen where the notes will move.
GREEN_NUMBER = 600000000  # The amount of time a note will spend on the screen before disappearing.
HIT_WINDOW = 100000000


class ChartData(object):
    """
    A chart object will be useful for passing chart data to functions.
    """

    def __init__(self, player, title, subtitle, artist, subartist, bpm, rank,
                 playlevel, total, stagefile, banner, difficulty, notecount, filepath, file, lnobj, md5):
        self.player = player
        self.title = title
        self.subtitle = subtitle
        self.artist = artist
        self.subartist = subartist
        self.bpm = bpm
        self.rank = rank
        self.playlevel = playlevel
        self.total = total
        self.stagefile = stagefile
        self.banner = banner
        self.difficulty = difficulty
        self.notecount = notecount
        self.filepath = filepath
        self.file = file
        self.lnobj = lnobj
        self.md5 = md5


LANE_ORDER = {
    # We want to translate the channels from the bms file to the actual lane order the player sees.
    "1": 2,
    "2": 3,
    "3": 4,
    "4": 5,
    "5": 6,
    "6": 1,
    "8": 7,
    "9": 8,
}

META = {
    # Exhaustive list of bms format commands. Most currently unimplemented.
    # First block - all besides total implemented.
    # Second block - only the p1visible implemented, the rest is planned.
    # Third block - mostly not planned besides landmines, lnobj, bpmxx and maybe random.
    "player": re.compile(r'(?<=#PLAYER )[1-4]$'),
    "genre": re.compile(r'(?<=#GENRE ).+$'),
    "title": re.compile(r'(?<=#TITLE ).+$'),
    "subtitle": re.compile(r'(?<=#SUBTITLE ).+$'),
    "artist": re.compile(r'(?<=#ARTIST ).+$'),
    "subartist": re.compile(r'(?<=#SUBARTIST ).+$'),
    "bpm": re.compile(r'(?<=#BPM )\d+(\.\d+)?$'),
    "playlevel": re.compile(r'(?<=#PLAYLEVEL )\d+(\.\d+)?$'),
    "total": re.compile(r'(?<=#TOTAL )\d+(\.\d+)?$'),
    "stagefile": re.compile(r'(?<=#STAGEFILE ).+$'),
    "rank": re.compile(r'(?<=#RANK )[0-3]$'),
    "banner": re.compile(r'(?<=#BANNER ).+$'),
    "difficulty": re.compile(r'(?<=#DIFFICULTY ).+$'),
    "wavxx": re.compile(r'(?<=#WAV)\w\w .+$'),
    "bmpxx": re.compile(r'(?<=#BMP)\w\w .+$'),
    #############################################
    "p1visible": re.compile(r'(?<=#)\d{3}1[1-9]:.+$'),
    "p2visible": re.compile(r'(?<=#)\d{3}2[1-9]:.+$'),
    "p1invisible": re.compile(r'(?<=#)\d{3}3[1-9]:.+$'),
    "p2invisible": re.compile(r'(?<=#)\d{3}4[1-9]:.+$'),
    "bgabase": re.compile(r'(?<=#)\d{3}04:.+$'),
    "bgapoor": re.compile(r'(?<=#)\d{3}06:.+$'),
    "bgm": re.compile(r'(?<=#)\d{3}01:.+$'),
    "meter": re.compile(r'(?<=#)\d{3}02:.+$'),
    #############################################
    "volwav": re.compile(r'(?<=#RANK )\d+$'),
    "defexrank": re.compile(r'(?<=#DEFEXRANK ).+$'),
    "backbmp": re.compile(r'(?<=#BACKBMP ).+$'),
    "charfile": re.compile(r'(?<=#CHARFILE ).+$'),
    "maker": re.compile(r'(?<=#MAKER ).+$'),
    "textxx": re.compile(r'(?<=#TEXT)\w\w .+$'),
    "songxx": re.compile(r'(?<=#SONG)\w\w .+$'),
    "exrankxx": re.compile(r'(?<=#EXRANK)\w\w \d+$'),
    "bpmxx": re.compile(r'(?<=#BPM)\w\w \d+$'),
    "exbpmxx": re.compile(r'(?<=#EXBPM)\w\w \d+$'),
    "stopxx": re.compile(r'(?<=#STOP)\w\w \d+$'),
    "changeoptionxx": re.compile(r'(?<=#CHANGEOPTION)\w\w .+$'),
    "exwavxx": re.compile(r'(?<=#EXWAV)\w\w .+$'),
    "exbmpxx": re.compile(r'(?<=#EXBMP)\w\w .+$'),
    "bgaxx": re.compile(r'(?<=#BGA)\w\w .+$'),
    "@bgaxx": re.compile(r'(?<=#@BGA)\w\w .+$'),
    "swbgaxx": re.compile(r'(?<=#SWBGA)\w\w .+$'),
    "argbxx": re.compile(r'(?<=#ARGB)\w\w .+$'),
    "seekxx": re.compile(r'(?<=#SEEK)\w\w \d+$'),
    "stp": re.compile(r'(?<=#STP )\d\d\d\.\d\d\d \d+$'),
    "landmine": re.compile(r'(?<=#)\d{3}[D-E][1-9]:.+$'),
    "pathwav": re.compile(r'(?<=#PATH_WAV ).+$'),
    "basebpm": re.compile(r'(?<=#BASEBPM )\d+$'),
    "lntype": re.compile(r'(?<=#LNTYPE )\d+$'),
    "lnobj": re.compile(r'(?<=#LNOBJ )\w+$'),
    "octfp": re.compile(r'#OCT/FP'),
    "option": re.compile(r'(?<=#OPTION ).+$'),
    "wavcmd": re.compile(r'(?<=#WAVCMD ).+$'),
    "cdda": re.compile(r'(?<=#CDDA )\d+$'),
    "midifile": re.compile(r'(?<=#MIDIFILE ).+$'),
    "poorbga": re.compile(r'(?<=#POORBGA )[0-2]+$'),
    "videofile": re.compile(r'(?<=#VIDEOFILE ).+$'),
    "videofs": re.compile(r'(?<=#VIDEOf/s )\d+$'),
    "videocolors": re.compile(r'(?<=#VIDEOCOLORS ).+$'),
    "videodly": re.compile(r'(?<=#VIDEODLY )\d+$'),
    "movie": re.compile(r'(?<=#MOVIE ).+$'),
    "extchr": re.compile(r'(?<=#ExtChr ).+$'),
    "materialswav": re.compile(r'(?<=#MATERIALSWAV ).+$'),
    "materialsbmp": re.compile(r'(?<=#MATERIALSBMP ).+$'),
    "divideprop": re.compile(r'(?<=#DIVIDEPROP )\d+$'),
    "charset": re.compile(r'(?<=#CHARSET ).+$'),
    "url": re.compile(r'(?<=%URL ).+$'),
    "email": re.compile(r'(?<=%EMAIL ).+$'),
    "random": re.compile(r'(?<=#RANDOM )\d+$'),
    "endrandom": re.compile(r'(?<=#ENDRANDOM )\d+$'),
    "rondam": re.compile(r'(?<=#RONDAM )\d+$'),
    "if": re.compile(r'(?<=#if )\d+$'),
    "endif": re.compile(r'#endif$'),
    "end_if": re.compile(r'#end if$'),
    "setrandom": re.compile(r'(?<=#SETRANDOM )\d+$'),
    "elseif": re.compile(r'(?<=#ELSEIF )\d+$'),
    "else": re.compile(r'#ELSE$'),
    "switch": re.compile(r'(?<=#SWITCH )\d+$'),
    "setswitch": re.compile(r'(?<=#SETSWITCH )\d+$'),
    "case": re.compile(r'(?<=#CASE )\d+$'),
    "def": re.compile(r'#DEF$'),
    "skip": re.compile(r'#SKIP$'),
    "endsw": re.compile(r'#ENDSW$'),
}


def parse_line(line):
    """
    A simple function used for searching for regex matches in a line.

    :param line: The line to be parsed.
    :return1: The key that was matched.
    :return2: The data from that line.
    """
    for key, rx in META.items():
        match = rx.search(line)
        if match:
            return key, match
        # if there are no matches
    return None, None


def parse_db(filepath, file):
    """
    Initially parses a file for metadata so that it can be displayed on the song select screen. Additionally,
    calculates the md5 checksum for score identification. The notecount will be wrong for ln and dp charts currently.
    :param filepath: The full path of the folder of the song
    :param file: The name of the bms file
    :return: a chart object containing metadata, filled with defaults if needed.
    """
    title = "No title"
    subtitle = ""
    artist = "No artist"
    subartist = ""
    difficulty = None
    rank = 2
    stagefile = None
    total = None
    banner = None
    lnobj = None
    playlevel = "3"

    notecount = 0

    # The game is primarily Japanese so everything is encoded with shift-jis.
    with open(filepath + file, 'r', encoding="shift-jis") as file_object:
        line = file_object.readline()

        while line:
            key, match = parse_line(line)
            if key == "player":
                player = match.group()
            if key == "title":
                title = match.group()
            if key == "subtitle":
                subtitle = match.group()
            if key == "artist":
                artist = match.group()
            if key == "subartist":
                subartist = match.group()
            if key == "bpm":
                bpm = float(match.group())
            if key == "rank":
                rank = int(match.group())
            if key == "playlevel":
                playlevel = match.group()
            if key == "total":
                total = float(match.group())
            if key == "stagefile":
                stagefile = match.group()
            if key == "banner":
                banner = match.group()
            if key == "difficulty":
                difficulty = int(match.group())

            if key == "p1visible":
                p1visible = match.group()
                p1visibledata = p1visible.strip().split(':', 1)[1]
                for i in range(0, len(p1visibledata) // 2):
                    if p1visibledata[0 + i * 2:2 + i * 2] != "00" and p1visibledata[0 + i * 2:2 + i * 2] != lnobj:
                        notecount += 1

            if key == "lnobj":
                lnobj = match.group()

            line = file_object.readline()

        with open(filepath + file, "rb") as f:
            md5 = hashlib.md5()
            while chunk := f.read(8192):
                md5.update(chunk)

        return ChartData(player, title, subtitle, artist, subartist, bpm,
                         rank, playlevel, total, stagefile, banner,
                         difficulty, notecount, filepath, file, lnobj, str(md5))


def parse(selected_chart):
    """
    The function used to parse the selected bms file again and load all the assets and timing data into memory.

    :param selected_chart: the selected chart object that we want to append sound and bga (unimplemented) data to.
    :type selected_chart: object
    :return: The selected chart with the asset lists added as atributes.
    """
    wavs = {}
    bmps = {}

    # The first frame will be empty to give the player some time to prepare
    # but mainly to avoid problems with measures 000 and 001
    p1visibles = [[]]
    bgms = [[]]

    # these are used to fill the measure list with empty measure if that measure
    # is completely empty (and in effect skipped in the bms file completely).
    p1visiblemax = bgmmax = 0
    with open(selected_chart.filepath + selected_chart.file, 'r', encoding="shift-jis") as file_object:
        line = file_object.readline()

        while line:
            key, match = parse_line(line)

            if key == "random" or key == "rondam":
                raise NotImplementedError("Unsupported command: random")

            if key == "wavxx":
                wavxx = match.group()
                wavindex, wavfile = wavxx.strip().split(' ', 1)
                if os.path.isfile(selected_chart.filepath + wavfile):
                    wavs[wavindex] = pygame.mixer.Sound(selected_chart.filepath + wavfile)
                elif os.path.isfile(selected_chart.filepath + wavfile[0:-4] + ".ogg"):
                    wavs[wavindex] = pygame.mixer.Sound(selected_chart.filepath + wavfile[0:-4] + ".ogg")

            if key == "bmpxx":
                bmpxx = match.group()
                bmpindex, bmpfile = bmpxx.strip().split(' ', 1)
                bmps[bmpindex] = bmpfile
                print(bmps[bmpindex])

            if key == "p1visible":
                p1visible = match.group()
                p1visibletime, p1visibledata = p1visible.strip().split(':', 1)
                p1visibletime, column = p1visibletime[:3], p1visibletime[4]
                p1visibletime = int(p1visibletime)
                while p1visiblemax < p1visibletime - 1:
                    p1visibles.append([])
                    p1visiblemax += 1
                if p1visibletime < len(p1visibles):
                    p1visibles[p1visibletime][column] = p1visibledata
                else:
                    p1visibles.append({column: p1visibledata})
                    p1visiblemax += 1

            if key == "bgm":
                bgm = match.group()
                bgmtime, bgmdata = bgm.strip().split(':', 1)
                bgmtime = bgmtime[0:3]
                bgmtime = int(bgmtime)
                while bgmmax < bgmtime - 1:
                    bgms.append([])
                    bgmmax += 1
                if bgmdata != "00":
                    if bgmtime < len(bgms):
                        bgms[bgmtime].append(bgmdata)
                    else:
                        bgms.append([bgmdata])
                        bgmmax += 1

            line = file_object.readline()

        selected_chart.__setattr__("wavs", wavs)
        selected_chart.__setattr__("p1visibles", p1visibles)
        selected_chart.__setattr__("bmps", bmps)
        selected_chart.__setattr__("bgms", bgms)

        return selected_chart


def keycheck_decide():
    """
    Handles the Pygame event queue in the decide screen.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()


def decide(selected_chart, screen, window):
    """
    The loading screen. Can display a stagefile if it is defined.
    :param selected_chart: The chart selected by the player. Some of it's parameters will be displayed on this screen.
    :param screen: The display surface.
    :param window: The rectangle of the screen.
    :return: the selected chart, the list of bgm events, the list of hittable notes, the total length of the song
    """

    # Setting up the surfaces before displaying them.
    start = time.perf_counter_ns()
    decide_font = pygame.font.Font("GenShinGothic-Medium.ttf", 70)
    artist_font = decide_font.render(selected_chart.artist + " " + selected_chart.subartist, True, "white")
    artist_rect = artist_font.get_rect()
    artist_rect.midbottom = window.midbottom
    title_font = decide_font.render(selected_chart.title + " " + selected_chart.subtitle, True, "white")
    title_rect = title_font.get_rect()
    title_rect.midbottom = artist_rect.midtop

    if selected_chart.stagefile is not None:
        stagefile_surface = pygame.image.load(selected_chart.filepath + selected_chart.stagefile)
        stagefile_surface = pygame.transform.scale(stagefile_surface, (
            int(window.height * 0.75 / stagefile_surface.get_height() * stagefile_surface.get_width()),
            int(window.height * 0.75)))
        stagefile_rect = stagefile_surface.get_rect()
        stagefile_rect.midtop = window.midtop

    # Displaying everything and flipping once.
    screen.fill("DarkSlateGray")
    if selected_chart.stagefile is not None:
        screen.blit(stagefile_surface, stagefile_rect)
    screen.blit(title_font, title_rect)
    screen.blit(artist_font, artist_rect)
    pygame.display.flip()
    selected_chart = parse(selected_chart)
    bgm_list, p1visible_list, total_time = divide(selected_chart)
    while time.perf_counter_ns() - start < 2000000000:  # if the loading takes less than two seconds, wait so that the
        # player can prepare.
        keycheck_decide()
    return selected_chart, bgm_list, p1visible_list, total_time


def keycheck_gameplay():
    column_list = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True
            if event.key == pygame.K_LSHIFT:
                column_list.append(1)
            if event.key == pygame.K_s:
                column_list.append(2)
            if event.key == pygame.K_d:
                column_list.append(3)
            if event.key == pygame.K_f:
                column_list.append(4)
            if event.key == pygame.K_SPACE:
                column_list.append(5)
            if event.key == pygame.K_j:
                column_list.append(6)
            if event.key == pygame.K_k:
                column_list.append(7)
            if event.key == pygame.K_l:
                column_list.append(8)
    return column_list


def keycheck_select():
    """
    Processes pygame events in the song select screen.
    :return: Music wheel movement / start a song / close the game / refresh the library / do nothing
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # those 2 move the song wheel up or down
            if event.key == pygame.K_UP:
                return -1
            if event.key == pygame.K_DOWN:
                return 1
            # starts the song
            if event.key == pygame.K_RETURN:
                return 2
            # closes the game
            if event.key == pygame.K_ESCAPE:
                return 3
            # refreshes the library
            if event.key == pygame.K_F5:
                return 4

        # the same thing as arrow keys but with mouse for convenience.
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                return -1
            elif event.button == 5:
                return 1
            if event.button == 1:
                return 2
    return 0


def keycheck_result():
    """
    Handles the Pygame event queue in the result screen.
    :return: Returns True when the player decides to leave the evaluation screen. False otherwise.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return True
    return False


def bgm_divide(chart, time_per_measure):
    """
    Divides bgm events from the string command format to a time-based list.
    :param chart: The chart object with the data
    :param time_per_measure: The time per one line of commands
    :return: A list of time values with corresponding lists of sound events
    """
    event_list = []
    for measure_counter, measure in enumerate(chart.bgms):
        if measure:
            for lane in measure:
                max_division = len(lane) // 2
                for i in range(0, max_division):
                    if lane[0 + i * 2:2 + i * 2] in chart.wavs:
                        note_time = int(measure_counter * time_per_measure + time_per_measure / max_division * i)
                        if lane[0 + i * 2:2 + i * 2] != "00":
                            new = True
                            for j, event in enumerate(event_list):
                                if event["time"] == note_time:
                                    new = False
                                    break
                            if new is True:
                                event_list.append({"time": note_time, "sound": [chart.wavs[lane[0 + i * 2:2 + i * 2]]]})
                            else:
                                event_list[j]["sound"].append(chart.wavs[lane[0 + i * 2:2 + i * 2]])
    return event_list


def p1visible_divide(chart, time_per_measure):
    """
    Divides events playable by a player from the string command format to a time-based list.
    :param chart: The chart object with the data
    :param time_per_measure: The time per one line of commands
    :return: A list of time values with corresponding column: note dictionaries
    """
    event_list = []
    for measure_counter, measure in enumerate(chart.p1visibles):
        if measure:
            for key, lane in measure.items():
                max_division = len(lane) // 2
                for i in range(0, max_division):
                    if lane[0 + i * 2:2 + i * 2] in chart.wavs:
                        note_time = int(measure_counter * time_per_measure + time_per_measure / max_division * i)
                        if lane[0 + i * 2:2 + i * 2] != "00" and lane[0 + i * 2:2 + i * 2] != chart.lnobj:
                            new = True
                            for j, event in enumerate(event_list):
                                if event["time"] == note_time:
                                    new = False
                                    break
                            if new is True:
                                event_list.append({"time": note_time, "notes": {key: chart.wavs[lane[0 + i * 2:2 + i * 2]]}})
                            else:
                                event_list[j]["notes"][key] = chart.wavs[lane[0 + i * 2:2 + i * 2]]
    return event_list


def divide(chart):
    """
    Calculates some useful data and forwards it to the divide functions. Only two of them so far but bmp_divide will
    also be made eventually.
    :param chart: The selected chart object
    :returns: The lists of bgms and hittable notes and the total length of the song.
    """
    # This is the default value of musical meter (4/4) but it can be changed in the bms file for any measure. That
    # possibility is not implemented yet.
    meter = 4
    end = max(len(chart.bgms), len(chart.p1visibles))
    total_time = int(((meter / chart.bpm * 60 * 1000000000) * end))
    time_per_measure = total_time // max(len(chart.bgms), len(chart.p1visibles))
    p1visible_list = p1visible_divide(chart, time_per_measure)
    bgm_list = bgm_divide(chart, time_per_measure)
    return bgm_list, p1visible_list, total_time


def draw_gameplay(window, screen, note_positions, judgements, current_time, current_judge, miss, miss_rect, great,
                  great_rect, bad, bad_rect):
    """
    Draws the entire gameplay screen and takes care of the positions of notes. Gives a miss judgement if a note goes too
    far down.
    :param window: The rectangle of the display surface
    :param screen: The display surface
    :param note_positions: A list of the current positions of notes
    :param judgements: A dictionary for counting the judgements the player gets
    :param current_time: The total time since the start of gameplay when the function is called
    :param current_judge: The judgement that is currently displayed on the screen
    :param miss: The miss judgement font surface
    :param miss_rect: The miss judgement font rect
    :param great: The great judgement font surface
    :param great_rect: The great judgement font rect
    :param bad: The bad judgement font surface
    :param bad_rect: The bad judgement font rect
    :returns: The list of judgements with misses added if any happened and the current judge
    """
    screen.fill("black")
    pygame.draw.rect(screen, "DarkSlateGray", Rect(window.width / 5, 0, window.width * 0.6, WHITE_NUMBER))
    for column, note_position in enumerate(note_positions):
        if note_position:
            for index, note in enumerate(note_position):
                # To give the notes the colors we want.
                if column + 1 == LANE_ORDER["1"] or column + 1 == LANE_ORDER["3"] or column + 1 == LANE_ORDER["5"]\
                        or column + 1 == LANE_ORDER["9"]:
                    pygame.draw.rect(screen, "white", note["rect"])
                elif column + 1 == LANE_ORDER["2"] or column + 1 == LANE_ORDER["4"] or column + 1 == LANE_ORDER["8"]:
                    pygame.draw.rect(screen, "blue", note["rect"])
                elif column + 1 == LANE_ORDER["6"]:
                    pygame.draw.rect(screen, "red", note["rect"])
                note_positions[column][index]["rect"].top = (
                        WHITE_NUMBER - ((note["time"] - current_time) / GREEN_NUMBER) * WHITE_NUMBER)
                if note["time"] + HIT_WINDOW < current_time:
                    del note_positions[column][index]
                    judgements["miss"] += 1
                    current_judge = {"time": current_time, "type": "miss"}
    if current_judge is not None:
        if current_time > current_judge["time"] + 500000000:
            current_judge = None
        elif current_judge["type"] == "miss":
            screen.blit(miss, miss_rect)
        elif current_judge["type"] == "bad":
            screen.blit(bad, bad_rect)
        elif current_judge["type"] == "great":
            screen.blit(great, great_rect)
    pygame.draw.rect(screen, "white", Rect(0, WHITE_NUMBER, window.width, 30))
    pygame.display.flip()
    return judgements, current_judge


def add_notes(column, window, note_positions, note_time):
    """
    Adds a note at the top of the screen when it's her time to shine!
    :param column: The column of the added note
    :param window: The rectangle of the display surface
    :param note_positions: The list of note positions on the screen
    :param note_time: The time when the note is supposed to be hit. NOT WHEN IT ENTERS THE SCREEN.
    :return: Returns the modified note positions list with a new note
    """
    # 8 is the number of columns.
    new_note = pygame.Rect(window.width / 5 + window.width * 0.6 / 8 * (LANE_ORDER[column] - 1), 0, 120, 50)
    note_positions[LANE_ORDER[column] - 1].append({"rect": new_note, "time": note_time})
    return note_positions[LANE_ORDER[column] - 1]


def update(bgm_list, p1visible_list, current_time, window, note_positions):
    """
    Manages pretty much everything that's independent from the player in gameplay
    :param bgm_list: The list of time values with corresponding bgm sounds
    :param p1visible_list: The list of time values with corresponding hittable notes
    :param current_time: The time at the moment the function is called
    :param window: The rectangle of the display surface
    :param note_positions: The list of note positions on the screen
    :return: The list of note positions.
    """
    for i, p1visible_event in enumerate(p1visible_list[0:9]):
        if p1visible_event["time"] < current_time + GREEN_NUMBER:
            for key, sound in p1visible_event["notes"].items():
                note_positions[LANE_ORDER[key] - 1] = add_notes(key, window, note_positions,
                                                                current_time + GREEN_NUMBER)
            del p1visible_list[i]
    for i, bgm_event in enumerate(bgm_list[0:9]):
        if bgm_event["time"] < current_time:
            for sound in bgm_event["sound"]:
                # We want to stop the sound and play it from the beginning if it is repeated before its end.
                if sound.get_num_channels() != 0:
                    sound.stop()
                sound.play()
            del bgm_list[i]
    return note_positions


def play_notes(column_list, note_positions, current_time, judgements, current_judge, p1visible_sounds,
               current_keysound):
    """
    Handles player interaction with the game - when a key is hit, a sound is played and a note may be hit as a result
    :param column_list: The list of keys hit by the player
    :param note_positions: Where the notes are on the screen
    :param current_time: The time since the screen was refreshed last time
    :param judgements: The amounts of each judgement received up to this point
    :param current_judge: The current judgement
    :param p1visible_sounds: The sounds playable by the player
    :param current_keysound: The keysound that is being played if no new note with matching time is found in
    p1visible_sounds. It's a list divided into columns
    :return: note position list, judgement counts, the current judge, the list of playable sounds, the keysound that was
    being played
    """
    for column in column_list:
        if p1visible_sounds[column - 1]:

            to_delete = None
            for index, sound_event in enumerate(p1visible_sounds[column - 1]):
                if sound_event["time"] - HIT_WINDOW < current_time < sound_event["time"] + HIT_WINDOW:
                    current_keysound[column - 1] = sound_event
                    to_delete = index
                    del note_positions[column - 1][0]
                    if -HIT_WINDOW / 2 < current_keysound[column - 1]["time"] - current_time < HIT_WINDOW / 2:
                        judgements["great"] += 1
                        current_judge = {"time": current_keysound[column - 1]["time"], "type": "great"}
                    elif -HIT_WINDOW < current_keysound[column - 1]["time"] - current_time < HIT_WINDOW:
                        judgements["bad"] += 1
                        current_judge = {"time": current_keysound[column - 1]["time"], "type": "bad"}
                    break
                elif sound_event["time"] - HIT_WINDOW <= current_time:
                    current_keysound[column - 1] = sound_event
                    to_delete = index
                elif current_time <= sound_event["time"] + HIT_WINDOW:
                    break
            if current_keysound[column - 1] is not None:
                # We want to stop the sound and play it from the beginning if it is repeated before its end.
                if current_keysound[column - 1]["sound"].get_num_channels() != 0:
                    current_keysound[column - 1]["sound"].stop()
                current_keysound[column - 1]["sound"].play()
            if to_delete is not None:
                del p1visible_sounds[column - 1][0:to_delete + 1]

    return note_positions, judgements, current_judge, p1visible_sounds, current_keysound


def eval_screen(window, screen, judgements, chart, score_db):
    """
    The screen where the player can see the full breakdown of their score. It is also saved here. Only the best scores
    are saved.
    :param window: The rectangle of the display surface
    :param screen: The display surface
    :param judgements: The amounts of each judgement received during gameplay
    :param chart: The chart that was being played
    :param score_db: The dictionary of all scores the player ever got.
    :return: The updated score database.
    """
    pygame.key.set_repeat()
    score = 0
    # Misses have a value of 0 points. The other weights are here:
    score += judgements["great"] * 2 + judgements["bad"]
    eval_font = pygame.font.Font("Roboto-Regular.ttf", 150)
    great = eval_font.render(f"GREAT: {judgements['great']}", True, BLUE)
    great_rect = great.get_rect()
    great_rect.topleft = (0, 0)
    bad = eval_font.render(f"BAD: {judgements['bad']}", True, PURPLE)
    bad_rect = bad.get_rect()
    bad_rect.topleft = great_rect.bottomleft
    miss = eval_font.render(f"MISS: {judgements['miss']}", True, RED)
    miss_rect = miss.get_rect()
    miss_rect.topleft = bad_rect.bottomleft
    result = eval_font.render(f"result: {score / (chart.notecount * 2) * 100:.2f}%", True, "white")
    result_rect = result.get_rect()
    result_rect.midleft = window.center
    if chart.md5 in score_db:
        if score > score_db[chart.md5]:
            score_db_file = open('scoredb.pkl', "wb")
            score_db[chart.md5] = score
            pickle.dump(score_db, score_db_file)
            score_db_file.close()
    else:
        score_db[chart.md5] = score
        score_db_file = open('scoredb.pkl', "wb")
        pickle.dump(score_db, score_db_file)
        score_db_file.close()
    while True:
        if keycheck_result() is True:
            break
        screen.fill("black")
        screen.blit(miss, miss_rect)
        screen.blit(great, great_rect)
        screen.blit(bad, bad_rect)
        screen.blit(result, result_rect)
        pygame.display.flip()
    return score_db


def load_charts():
    """
    Opens or creates a database of all bms songs a player has.
    :return: A list of chart objects of all songs in the directory of the game.
    """
    chart_list = []
    if not os.path.isfile('db.pkl'):
        for subdir, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
            for file in files:
                filepath = subdir + os.sep
                if file.endswith(".bms") or file.endswith(".bme") or file.endswith(".bml"):
                    chart_list.append(parse_db(filepath, file))
        db = open("db.pkl", 'wb')
        pickle.dump(chart_list, db)
        db.close()
    else:
        db = open("db.pkl", 'rb')
        chart_list = pickle.load(db)
        db.close()
    return chart_list


DIFFICULTY_COLOR = {
    # Just a simple dictionary of font colors on the song select screen.
    1: "LawnGreen",
    2: "DeepSkyBlue",
    3: "Yellow",
    4: "Red",
    5: "Purple"
}


def song_select(screen, window, score_db, index):
    """
    Draws and manages the song select screen.
    This function is a moloch but honestly, I will need to break it down.
    :param window: The rectangle of the display surface
    :param screen: The display surface
    :param score_db: A dictionary of all scores the player ever got
    :param index: The current position of the song wheel
    :return: Either returns the selected chart and it's position on the song wheel or the command to quit from the game
    or to rebuild the song database.
    """
    pygame.mixer.stop()  # We don't want the sounds from gameplay to last in song select if the player quits early.
    pygame.key.set_repeat(50, 50)  # for scrolling through songs.
    chart_list = load_charts()
    if not chart_list:
        raise FileNotFoundError("You need to install at least one song to use this game! "
                                "Visit https://github.com/wcko87/beatoraja-english-guide/wiki/Downloading-Songs"
                                " to learn more. Put the song's folder somewhere in the root folder of this game!")
    select_font = pygame.font.Font("GenShinGothic-Medium.ttf", 70)
    for chart in chart_list:
        # Setting up surfaces before displaying them.
        if chart.difficulty in DIFFICULTY_COLOR:
            color = DIFFICULTY_COLOR[chart.difficulty]
        else:
            color = "grey"

        chart.__setattr__("title_font", select_font.render(chart.title + " " + chart.subtitle, True, color))
        if chart.title_font.get_width() > window.width / 3 * 2:
            chart.title_font = pygame.transform.smoothscale(chart.title_font,
                                                            (window.width // 3 * 2, chart.title_font.get_height()))
        chart.__setattr__("artist_font", select_font.render(chart.artist + " " + chart.subartist, True, color))
        if chart.artist_font.get_width() > window.width / 3 * 2:
            chart.artist_font = pygame.transform.smoothscale(chart.artist_font,
                                                             (window.width // 3 * 2, chart.artist_font.get_height()))
        chart.__setattr__("playlevel_font", select_font.render(chart.playlevel, True, color))
        chart.__setattr__("diff_font", select_font.render(str(chart.difficulty), True, "white"))
        chart.__setattr__("notecount_font", select_font.render(str(chart.notecount), True, "white"))
        chart.__setattr__("total_font", select_font.render(str(chart.total), True, "white"))
        chart.__setattr__("playlevel_font", select_font.render(str(chart.playlevel), True, color))
    while True:
        screen.fill("DarkSlateGray")
        pygame.draw.rect(screen, "DimGray", Rect(window.width / 3, 0, window.width / 3 * 2, window.height))

        # The first menu item is drawn separately from other ones to set the origin.
        chart_list[index].__setattr__("title_rect", chart_list[index].title_font.get_rect())
        chart_list[index].title_rect.topleft = (window.width / 3, 0)

        chart_list[index].__setattr__("artist_rect", chart_list[index].artist_font.get_rect())
        chart_list[index].artist_rect.topright = (window.width, chart_list[index].title_rect.bottom)

        playlevel_rect = chart_list[index].playlevel_font.get_rect()
        playlevel_rect.center = (
            chart_list[index].title_rect.left - window.width // 48, chart_list[index].title_rect.bottom)

        # in the rare case that the first displayed song is also the third song
        # (happens when the player has less than 3 songs).
        if index == (index + 2) % len(chart_list):
            pygame.draw.rect(screen, "maroon",
                             Rect(window.width / 3, chart_list[index].title_rect.top, window.width / 3 * 2,
                                  chart_list[index].title_rect.height + chart_list[index].artist_rect.height))

        # The nice line behind difficulty numbers.
        pygame.draw.rect(screen, "maroon",
                         Rect(window.width / 3 - window.width // 24, chart_list[index].title_rect.top,
                              window.width // 24,
                              chart_list[index].title_rect.height + window.height))

        screen.blit(chart_list[index].playlevel_font, playlevel_rect)
        screen.blit(chart_list[index].title_font, chart_list[index].title_rect)
        screen.blit(chart_list[index].artist_font, chart_list[index].artist_rect)

        # This is for all items that are not the first one.
        for i in range(index + 1, index + 10):
            if i >= len(chart_list):
                i = i % len(chart_list)
            chart_list[i].__setattr__("title_rect", chart_list[i].title_font.get_rect())
            chart_list[i].title_rect.topleft = (window.width / 3, chart_list[i - 1].artist_rect.bottom)
            chart_list[i].__setattr__("artist_rect", chart_list[i].artist_font.get_rect())
            chart_list[i].artist_rect.topright = (window.width, chart_list[i].title_rect.bottom)

            # Currently selected and highlighted song.
            if i == (index + 2) % len(chart_list):
                if chart_list[i].banner is not None:
                    banner_surface = pygame.image.load(chart_list[i].filepath + chart_list[i].banner)
                    # scales the banner up but keeps the aspect ratio.
                    banner_surface = pygame.transform.scale(banner_surface, (int(window.width / 3 - window.width // 24),
                                                                             int((
                                                                                         window.width / 3 - window.width // 24) / banner_surface.get_width() * banner_surface.get_height())))
                    banner_rect = banner_surface.get_rect()
                    banner_rect.topleft = (0, 0)
                    screen.blit(banner_surface, banner_rect)
                # The number of hittable notes a song has.
                notecount_font = select_font.render("Notes: " + str(chart_list[i].notecount), True, "white")
                notecount_rect = notecount_font.get_rect()
                notecount_rect.midleft = window.midleft
                screen.blit(notecount_font, notecount_rect)

                # Shows what score the player has on the highlighted song.
                if chart_list[i].md5 in score_db:
                    score_font = select_font.render(
                        f"Best: {score_db[chart_list[i].md5] / (chart_list[i].notecount * 2) * 100:.2f}%", True,
                        "white")
                    score_rect = score_font.get_rect()
                    score_rect.bottomleft = window.bottomleft
                    screen.blit(score_font, score_rect)

                pygame.draw.rect(screen, "maroon",
                                 Rect(window.width / 3, chart_list[i].title_rect.top, window.width / 3 * 2,
                                      chart_list[i].title_rect.height + chart_list[i].artist_rect.height))
            playlevel_rect = chart_list[i].playlevel_font.get_rect()
            playlevel_rect.center = (
                chart_list[i].title_rect.left - window.width // 48, chart_list[i].title_rect.bottom)
            pygame.draw.rect(screen, "maroon", Rect(window.width / 3 - window.width // 24, chart_list[i].title_rect.top,
                                                    window.width // 24,
                                                    chart_list[i].title_rect.height + window.height))
            screen.blit(chart_list[i].playlevel_font, playlevel_rect)
            screen.blit(chart_list[i].title_font, chart_list[i].title_rect)
            screen.blit(chart_list[i].artist_font, chart_list[i].artist_rect)

        pygame.display.flip()

        command = keycheck_select()
        if command in range(-1, 2):
            index += command
            index %= len(chart_list)
        elif command == 2:
            return chart_list[(index + 2) % len(chart_list)], index
        elif command == 3:
            return "quit"
        elif command == 4:
            return "rebuild"


def p1visible_sounds_divide(p1visible_list):
    """
    :param p1visible_list: The list of hittable notes with their times.
    :return: A list of playable sounds with their times.
    """
    p1visible_sounds = [[], [], [], [], [], [], [], []]
    for i, p1visible_event in enumerate(p1visible_list):
        for key, sound in p1visible_event["notes"].items():
            p1visible_sounds[LANE_ORDER[key] - 1].append({"sound": sound, "time": p1visible_list[i]["time"]})
    return p1visible_sounds


def gameplay(window, screen, bgm_list, p1visible_list, chart, score_db, total_time):
    """
    The main gameplay loop. Sets some initial values and runs everything, supplying functions with the current time.
    :param window: The rectangle of the display surface
    :param screen: The display surface
    :param bgm_list: The list of time values with corresponding bgm sounds
    :param p1visible_list: The list of time values with corresponding hittable notes
    :param chart: The selected chart to be played.
    :param score_db: A dictionary of all scores the player ever got
    :param total_time: The total length of the song and in effect, the length of the gameplay loop.
    :return: The score database, updated.
    """
    pygame.key.set_repeat()
    note_positions = [[], [], [], [], [], [], [], []]
    start = time.perf_counter_ns()
    judgements = {"great": 0, "bad": 0, "miss": 0}
    gameplay_font = pygame.font.Font("Roboto-Regular.ttf", 150)
    great = gameplay_font.render("GREAT", True, BLUE)
    great_rect = great.get_rect()
    great_rect.midtop = window.midtop
    bad = gameplay_font.render("BAD", True, PURPLE)
    bad_rect = bad.get_rect()
    bad_rect.midtop = window.midtop
    miss = gameplay_font.render("MISS", True, RED)
    miss_rect = miss.get_rect()
    miss_rect.midtop = window.midtop
    current_judge = None
    p1visible_sounds = p1visible_sounds_divide(p1visible_list)
    current_keysound = [None, None, None, None, None, None, None, None]
    # Setting up the initial sounds for each column:
    for i, keysound in enumerate(current_keysound):
        if p1visible_sounds[i]:
            current_keysound[i] = p1visible_sounds[i][0]
    force_quit = False
    while time.perf_counter_ns() - start < total_time + 2000000000:
        note_positions = update(bgm_list, p1visible_list, time.perf_counter_ns() - start, window,
                                note_positions)
        judgements, current_judge = draw_gameplay(window, screen, note_positions, judgements,
                                                  time.perf_counter_ns() - start, current_judge, miss, miss_rect, great,
                                                  great_rect, bad, bad_rect)
        current_time = time.perf_counter_ns() - start
        command = keycheck_gameplay()
        if type(command) is list:
            column_list = command
        elif command is True:
            force_quit = True
            break
        if column_list:
            note_positions, judgements, current_judge, p1visible_sounds, current_keysound = play_notes(column_list,
                                                                                                       note_positions,
                                                                                                       current_time,
                                                                                                       judgements,
                                                                                                       current_judge,
                                                                                                       p1visible_sounds,
                                                                                                       current_keysound)
    if force_quit is False:
        score_db = eval_screen(window, screen, judgements, chart, score_db)
    return score_db


def main():
    """The main function of the program"""
    if os.path.isfile('scoredb.pkl'):
        score_db_file = open('scoredb.pkl', 'rb')
        score_db = pickle.load(score_db_file)
    else:
        score_db = {}

    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
    pygame.mixer.set_num_channels(100)
    pygame.init()
    pygame.event.set_allowed((pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN, pygame.QUIT))
    pygame.font.init()
    screen = pygame.display.set_mode((1920, 1080), HWSURFACE)  # Hardware acceleration flag.
    screen.set_alpha(None)
    window = screen.get_rect()
    index = 0  # The starting position on the song select screen.
    while True:
        command = song_select(screen, window, score_db, index)
        if command == "quit" or command == "rebuild":
            break
        else:
            selected_chart, index = command
        chart, bgm_list, p1visible_list, total_time = decide(selected_chart, screen, window)
        score_db = gameplay(window, screen, bgm_list, p1visible_list, chart, score_db, total_time)
    pygame.quit()
    if command == "rebuild":
        os.remove("db.pkl")
        os.system('main.py')


if __name__ == "__main__":
    main()
