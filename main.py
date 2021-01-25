import pygame
import sys
import re
import time
import os
import pickle
from pygame.locals import *

BLACK = (0, 0, 0)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)
WHITE = (255, 255, 255)
BLUE = (0, 255, 255)
DESIRED_DT = 600000
WHITE_NUMBER = 1000
GREEN_NUMBER = 600000000
HIT_WINDOW = 60000000


class ChartData(object):
    """
    A chart object will be useful for passing chart data to functions.
    """
    # The values passed can be None but it doesn't matter.
    def __init__(self, player, title, subtitle, artist, subartist, bpm, rank,
                 playlevel, total, stagefile, banner, difficulty, wavs,
                 bmps, p1visibles, bgms, lnobj, notecount, filepath, file):
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
        self.wavs = wavs
        self.bmps = bmps
        self.p1visibles = p1visibles
        self.bgms = bgms
        self.lnobj = lnobj
        self.notecount = notecount
        self.filepath = filepath
        self.file = file


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
    "player": re.compile(r'(?<=#PLAYER )[1-4]$'),
    "genre": re.compile(r'(?<=#GENRE ).+$'),
    "title": re.compile(r'(?<=#TITLE ).+$'),
    "subtitle": re.compile(r'(?<=#SUBTITLE ).+$'),
    "artist": re.compile(r'(?<=#ARTIST ).+$'),
    "subartist": re.compile(r'(?<=#SUBARTIST ).+$'),
    "bpm": re.compile(r'(?<=#BPM )\d+$'),
    "playlevel": re.compile(r'(?<=#PLAYLEVEL )\d+$'),
    "total": re.compile(r'(?<=#TOTAL )\d+$'),
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
    title = "No title"
    subtitle = ""
    subartist = ""
    # stagefile = None
    # banner = None
    difficulty = None
    lnobj = None
    rank = 2
    stagefile = None
    total = None
    banner = None
    playlevel = "3"

    notecount = 0
    with open(filepath + file, 'r') as file_object:
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
                total = int(match.group())
            if key == "stagefile":
                stagefile = match.group()
            if key == "banner":
                banner = pygame.image.load(filepath + match.group())
            if key == "difficulty":
                difficulty = int(match.group())

            if key == "p1visible":
                p1visible = match.group()
                p1visibledata = p1visible.strip().split(':', 1)[1]
                for i in range(0, len(p1visibledata) // 2):
                    if p1visibledata[0 + i * 2:2 + i * 2]:
                        notecount += 1

            if key == "lnobj":
                lnobj = match.group()
                print("lnobj: " + lnobj)

            line = file_object.readline()

        return ChartData(player, title, subtitle, artist, subartist, bpm,
                         rank, playlevel, total, stagefile, banner,
                         difficulty, wavs=None, bmps=None, p1visibles=None, bgms=None, lnobj=None, notecount=notecount, filepath=filepath, file=file)


def parse(filepath, file):
    """
    The function used to parse the bms file into internal objects and variables

    Parameters:
    file (string): the path to the file that is to be parsed
    """
    wavs = {}
    bmps = {}
    p1visibles = []
    bgms = []

    title = "No title"
    subtitle = ""
    subartist = ""
    # stagefile = None
    # banner = None
    difficulty = None
    lnobj = None
    rank = 2
    stagefile = None
    total = None
    banner = None
    playlevel = 3
    p1visiblemax = bgmmax = 1
    with open(filepath + file, 'r') as file_object:
        line = file_object.readline()

        while line:
            key, match = parse_line(line)
            if key == "player":
                player = match.group()
                print("player: " + player)
            if key == "title":
                title = match.group()
                print("title: " + title)
            if key == "subtitle":
                subtitle = match.group()
                print("subtitle: " + subtitle)
            if key == "artist":
                artist = match.group()
                print("artist: " + artist)
            if key == "subartist":
                subartist = match.group()
                print("subartist: " + subartist)
            if key == "bpm":
                bpm = float(match.group())
            if key == "rank":
                rank = int(match.group())
                print("rank: ", rank)
            if key == "playlevel":
                playlevel = match.group()
                print("playlevel: " + playlevel)
            if key == "total":
                total = int(match.group())
                print("total: ", total)
            if key == "stagefile":
                stagefile = match.group()
                print("stagefile: " + stagefile)
            if key == "banner":
                banner = match.group()
                print("banner: " + banner)
            if key == "difficulty":
                difficulty = int(match.group())
                print("difficulty: ", difficulty)
            if key == "random" or key == "rondam":
                raise NameError("Unsupported command: random")

            if key == "wavxx":
                wavxx = match.group()
                wavindex, wavfile = wavxx.strip().split(' ', 1)
                wavs[wavindex] = pygame.mixer.Sound(filepath + wavfile)

            if key == "bmpxx":
                bmpxx = match.group()
                bmpindex, bmpfile = bmpxx.strip().split(' ', 1)
                bmps[bmpindex] = bmpfile
                print(bmps[bmpindex])

            if key == "p1visible":
                p1visible = match.group()
                p1visibletime, p1visibledata = p1visible.strip().split(':', 1)
                p1visibletime, lane = p1visibletime[:3], p1visibletime[4]
                p1visibletime = int(p1visibletime)
                while p1visiblemax < p1visibletime - 1:
                    p1visibles.append([])
                    p1visiblemax += 1
                if p1visibletime < len(p1visibles):
                    p1visibles[p1visibletime][lane] = p1visibledata
                else:
                    p1visibles.append({lane: p1visibledata})
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

            if key == "lnobj":
                lnobj = match.group()
                print("lnobj: " + lnobj)

            line = file_object.readline()

        return ChartData(player, title, subtitle, artist, subartist, bpm,
                         rank, playlevel, total, stagefile, banner,
                         difficulty, wavs, bmps, p1visibles, bgms, lnobj, notecount=None, filepath=filepath, file=None)


def get_keys():
    key = pygame.key.get_pressed()
    column_list = []
    if key[K_s]:
        column_list.append(2)
    if key[K_d]:
        column_list.append(3)
    if key[K_f]:
        column_list.append(4)
    if key[K_SPACE]:
        column_list.append(5)
    if key[K_j]:
        column_list.append(6)
    if key[K_k]:
        column_list.append(7)
    if key[K_l]:
        column_list.append(8)
    if key[K_LSHIFT]:
        column_list.append(1)
    return column_list


def keycheck_gameplay():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True
    column_list = get_keys()
    return column_list


def keycheck_select():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                return -1
            if event.key == pygame.K_DOWN:
                return 1
            if event.key == pygame.K_RETURN:
                return 2
            if event.key == pygame.K_ESCAPE:
                return 3
    return 0


def keycheck_result():
    """
    Handles the Pygame event queue in the result screen.
    :return:
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return True
    return False


def bgm_divide(chart, time_per_measure, total_time):
    event_list = []
    for measure_counter, measure in enumerate(chart.bgms):
        if measure:
            for lane in measure:
                max_division = len(lane) // 2
                for i in range(0, max_division):
                    if lane[0 + i * 2:2 + i * 2] in chart.wavs:
                        note_time = int(measure_counter * time_per_measure + time_per_measure / max_division * i)
                        if lane[0 + i * 2:2 + i * 2] != "00" and lane[0 + i * 2:2 + i * 2] != chart.lnobj:
                            new = True
                            for j, event in enumerate(event_list):
                                if event[0] == note_time:
                                    new = False
                                    break
                            if new is True:
                                event_list.append([note_time, [chart.wavs[lane[0 + i * 2:2 + i * 2]]]])
                            else:
                                event_list[j][1].append(chart.wavs[lane[0 + i * 2:2 + i * 2]])
    return event_list


def p1visible_divide(chart, time_per_measure, total_time):
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
                                if event[0] == note_time:
                                    new = False
                                    break
                            if new is True:
                                event_list.append([note_time, {key: chart.wavs[lane[0 + i * 2:2 + i * 2]]}])
                            else:
                                event_list[j][1][key] = chart.wavs[lane[0 + i * 2:2 + i * 2]]
    return event_list


def divide(chart):
    meter = 4
    end = max(len(chart.bgms), len(chart.p1visibles))
    # amount of desired dts per measure
    total_time = int(((meter / chart.bpm * 60 * 1000000000) * end))
    print("length: " + str(total_time))
    time_per_measure = total_time // len(chart.p1visibles)
    p1visible_list = p1visible_divide(chart, time_per_measure, total_time)
    bgm_list = bgm_divide(chart, time_per_measure, total_time)
    return bgm_list, p1visible_list, total_time


def draw_notes(window, screen, note_positions, judgements, current_time, current_judge, miss, miss_rect, great, great_rect, bad, bad_rect):
    pygame.draw.rect(screen, "DarkSlateGray", Rect(window.width / 5, 0, window.width * 0.6, WHITE_NUMBER))
    for column, note_position in enumerate(note_positions):
        if note_position:
            for index, note in enumerate(note_position):
                if column + 1 == 2 or column + 1 == 4 or column + 1 == 6 or column + 1 == 8:
                    pygame.draw.rect(screen, "white", note["rect"])
                elif column + 1 == 3 or column + 1 == 5 or column + 1 == 7:
                    pygame.draw.rect(screen, "blue", note["rect"])
                elif column + 1 == 1:
                    pygame.draw.rect(screen, "red", note["rect"])
                note_positions[column][index]["rect"].top = (WHITE_NUMBER - ((note["time"] - current_time) / GREEN_NUMBER) * WHITE_NUMBER)
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
    # 8 is the number of columns.
    new_note = pygame.Rect(window.width / 5 + window.width * 0.6 / 8 * (LANE_ORDER[column] - 1), 0, 100, 50)
    note_positions[LANE_ORDER[column] - 1].append({"rect": new_note, "time": note_time})
    return note_positions[LANE_ORDER[column] - 1]


def update(screen, bgm_list, p1visible_list, current_time, window, note_positions):
    screen.fill(BLACK)
    for i, p1visible_event in enumerate(p1visible_list[0:9]):
        if p1visible_event[0] < current_time + GREEN_NUMBER:
            for key, sound in p1visible_event[1].items():
                note_positions[LANE_ORDER[key] - 1] = add_notes(key, window, note_positions, current_time + GREEN_NUMBER)
            del p1visible_list[i]
    for i, bgm_event in enumerate(bgm_list[0:9]):
        if bgm_event[0] < current_time:
            for sound in bgm_event[1]:
                sound.play()
            del bgm_list[i]
    return note_positions


def play_notes(column_list, note_positions, current_time, judgements, ignore_list, current_judge, p1visible_sounds, current_keysound):
    for column in column_list:
        if p1visible_sounds[column-1] and (column not in ignore_list):
            to_delete = None
            for index, sound_event in enumerate(p1visible_sounds[column-1]):
                if sound_event["time"] - HIT_WINDOW < current_time < sound_event["time"] + HIT_WINDOW:
                    current_keysound[column-1] = sound_event
                    to_delete = index
                    del note_positions[column-1][0]
                    if -HIT_WINDOW / 2 < current_keysound[column-1]["time"] - current_time < HIT_WINDOW / 2:
                        judgements["great"] += 1
                        current_judge = {"time": current_keysound[column-1]["time"], "type": "great"}
                    elif -HIT_WINDOW < current_keysound[column-1]["time"] - current_time < HIT_WINDOW:
                        judgements["bad"] += 1
                        current_judge = {"time": current_keysound[column-1]["time"], "type": "bad"}
                    break
                elif sound_event["time"] - HIT_WINDOW <= current_time:
                    current_keysound[column - 1] = sound_event
                    to_delete = index
                elif current_time <= sound_event["time"] + HIT_WINDOW:
                    break
            if current_keysound[column-1] is not None:
                current_keysound[column-1]["sound"].play()
            if column not in ignore_list:
                ignore_list.append(column)
            if to_delete is not None:
                del p1visible_sounds[column-1][0:to_delete+1]

    return ignore_list, note_positions, judgements, current_judge, p1visible_sounds, current_keysound


def eval_screen(window, screen, judgements):
    score = 0
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
    result = eval_font.render(f"result: {score / ((judgements['great'] + judgements['bad'] + judgements['miss']) * 2) * 100:.2f}%", True, WHITE)
    result_rect = result.get_rect()
    result_rect.midleft = window.center
    while True:
        if keycheck_result() is True:
            break
        screen.fill(BLACK)
        screen.blit(miss, miss_rect)
        screen.blit(great, great_rect)
        screen.blit(bad, bad_rect)
        screen.blit(result, result_rect)
        pygame.display.flip()


def load_charts():
    chart_list = []
    # I can't pickle pygame surfaces so db creation is currently unfinished.
    if not os.path.isfile('db.pkl'):
        for subdir, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
            for file in files:
                filepath = subdir + os.sep
                if file.endswith(".bms") or file.endswith(".bme") or file.endswith(".bml"):
                    chart_list.append(parse_db(filepath, file))
        # db = open("db.pnl", 'wb')
        # pickle.dump(chart_list, db)
    # else:
        # db = open("db.pnl", 'rb')
        # chart_list = pickle.load(db)
    return chart_list


def song_select(screen, window):
    chart_list = load_charts()
    select_font = pygame.font.Font("GenShinGothic-Medium.ttf", 70)
    for chart in chart_list:
        if chart.difficulty == 1:
            color = "LawnGreen"
        elif chart.difficulty == 2:
            color = "DeepSkyBlue"
        elif chart.difficulty == 3:
            color = "Yellow"
        elif chart.difficulty == 4:
            color = "Red"
        elif chart.difficulty == 5:
            color = "Purple"
        else:
            color = "Grey"
        chart.__setattr__("title_font", select_font.render(chart.title + " " + chart.subtitle, True, color))
        if chart.title_font.get_width() > window.width / 3 * 2:
            chart.title_font = pygame.transform.smoothscale(chart.title_font, (window.width // 3 * 2, chart.title_font.get_height()))
        chart.__setattr__("artist_font", select_font.render(chart.artist + " " + chart.subartist, True, color))
        if chart.artist_font.get_width() > window.width / 3 * 2:
            chart.artist_font = pygame.transform.smoothscale(chart.artist_font, (window.width // 3 * 2, chart.artist_font.get_height()))
        chart.__setattr__("playlevel_font", select_font.render(chart.playlevel, True, color))
        chart.__setattr__("diff_font", select_font.render(str(chart.difficulty), True, "white"))
        chart.__setattr__("notecount_font", select_font.render(str(chart.notecount), True, "white"))
        chart.__setattr__("total_font", select_font.render(str(chart.total), True, "white"))
    index = 0
    while True:
        screen.fill("DarkSlateGray")
        pygame.draw.rect(screen, "DimGray", Rect(window.width / 3, 0, window.width / 3 * 2, window.height))
        chart_list[index].__setattr__("title_rect", chart_list[index].title_font.get_rect())
        chart_list[index].title_rect.topleft = (window.width / 3, 0)
        chart_list[index].__setattr__("artist_rect", chart_list[index].artist_font.get_rect())
        chart_list[index].artist_rect.topright = (window.width, chart_list[index].title_rect.bottom)
        screen.blit(chart_list[index].title_font, chart_list[index].title_rect)
        screen.blit(chart_list[index].artist_font, chart_list[index].artist_rect)
        for i in range(index + 1, index + 10):
            if i >= len(chart_list):
                i = i % len(chart_list)
            chart_list[i].__setattr__("title_rect", chart_list[i].title_font.get_rect())
            chart_list[i].title_rect.topleft = (window.width / 3, chart_list[i-1].artist_rect.bottom)
            chart_list[i].__setattr__("artist_rect", chart_list[i].artist_font.get_rect())
            chart_list[i].artist_rect.topright = (window.width, chart_list[i].title_rect.bottom)
            if i == (index + 2) % len(chart_list):
                pygame.draw.rect(screen, "gold", Rect(window.width / 3, chart_list[i].title_rect.top, window.width / 3 * 2, chart_list[i].title_rect.height + chart_list[i].artist_rect.height))
            screen.blit(chart_list[i].title_font, chart_list[i].title_rect)
            screen.blit(chart_list[i].artist_font, chart_list[i].artist_rect)
        pygame.display.flip()
        command = keycheck_select()
        if command in range(-1, 2):
            index += command
            index %= len(chart_list)
        elif command == 2:
            return chart_list[(index + 2) % len(chart_list)].filepath, chart_list[(index + 2) % len(chart_list)].file
        elif command == 3:
            return "quit"


def p1visible_sounds_divide(p1visible_list):
    p1visible_sounds = [[], [], [], [], [], [], [], []]
    for i, p1visible_event in enumerate(p1visible_list):
        for key, sound in p1visible_event[1].items():
            p1visible_sounds[LANE_ORDER[key]-1].append({"sound": sound, "time": p1visible_list[i][0]})
    return p1visible_sounds


def gameplay(window, screen, bgm_list, p1visible_list):
    note_positions = [[], [], [], [], [], [], [], []]
    start = time.perf_counter_ns()
    judgements = {"great": 0, "bad": 0, "miss": 0}
    ignore_list = []
    end = max(p1visible_list[-1][0], bgm_list[-1][0])
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
    current_keysound = [None, None, None, None, None, None, None, None]
    p1visible_sounds = p1visible_sounds_divide(p1visible_list)
    force_quit = False
    while time.perf_counter_ns() - start < end + 2000000000:
        note_positions = update(screen, bgm_list, p1visible_list, time.perf_counter_ns() - start, window,
                                note_positions)
        judgements, current_judge = draw_notes(window, screen, note_positions, judgements, time.perf_counter_ns() - start, current_judge, miss, miss_rect, great, great_rect, bad, bad_rect)
        command = keycheck_gameplay()
        if type(command) is list:
            column_list = command
        elif command is True:
            force_quit = True
            break
        if column_list is not None:
            for column in ignore_list:
                if column not in column_list:
                    ignore_list.remove(column)
            ignore_list, note_positions, judgements, current_judge, p1visible_sounds, current_keysound = play_notes(column_list, note_positions, time.perf_counter_ns() - start, judgements, ignore_list, current_judge, p1visible_sounds, current_keysound)
    if force_quit is False:
        eval_screen(window, screen, judgements)


def main():
    """The main function of the program"""
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
    pygame.mixer.set_num_channels(100)
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1920, 1080), DOUBLEBUF | HWSURFACE)
    screen.set_alpha(None)
    window = screen.get_rect()
    while True:
        command = song_select(screen, window)
        if command == "quit":
            break
        else:
            filepath, file = command
        chart = parse(filepath, file)
        bgm_list, p1visible_list, total_time = divide(chart)
        gameplay(window, screen, bgm_list, p1visible_list)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
