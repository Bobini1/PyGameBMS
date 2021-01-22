import pygame
import sys
import re
import time
from pygame.locals import *

BLACK = (0, 0, 0)
DESIRED_DT = 600000
PATH = r"C:\Users\PC\PycharmProjects\PygameBMS\J219"
WHITE_NUMBER = 1000000000
HIT_WINDOW = 20000000

class ChartData(object):
    # The values passed can be None but it doesn't matter.
    def __init__(self, player, title, subtitle, artist, subartist, bpm, rank,
                 playlevel, total, stagefile, banner, difficulty, wavs,
                 bmps, p1visibles, bgms, lnobj):
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


LANE_ORDER = {
    "1": 2,
    "2": 3,
    "3": 4,
    "4": 5,
    "5": 6,
    "6": 1,
    "8": 7,
    "9": 8,
}

meta = {
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
    for key, rx in meta.items():
        match = rx.search(line)
        if match:
            return key, match
        # if there are no matches
    return None, None


def parse(file):
    """
    The function used to parse the bms file into internal objects and variables

    Parameters:
    file (string): the path to the file that is to be parsed
    """
    wavs = {}
    bmps = {}
    p1visibles = []
    bgms = []

    subtitle = None
    subartist = None
    stagefile = None
    banner = None
    difficulty = None
    lnobj = None
    rank = None
    stagefile = None
    total = None
    banner = None
    playlevel = None
    p1visiblemax = bgmmax = 1
    with open(file, 'r') as file_object:
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
                rank = match.group()
                print("rank: " + rank)
            if key == "playlevel":
                playlevel = match.group()
                print("playlevel: " + playlevel)
            if key == "total":
                total = match.group()
                print("total: " + total)
            if key == "stagefile":
                stagefile = match.group()
                print("stagefile: " + stagefile)
            if key == "banner":
                banner = match.group()
                print("banner: " + banner)
            if key == "difficulty":
                difficulty = match.group()
                print("difficulty: " + difficulty)
            if key == "random" or key == "rondam":
                raise NameError("Unsupported command")

            if key == "wavxx":
                wavxx = match.group()
                wavindex, wavfile = wavxx.strip().split(' ')
                wavs[wavindex] = pygame.mixer.Sound(PATH + "\\" + wavfile)

            if key == "bmpxx":
                bmpxx = match.group()
                bmpindex, bmpfile = bmpxx.strip().split(' ')
                bmps[bmpindex] = bmpfile
                print(bmps[bmpindex])

            if key == "p1visible":
                p1visible = match.group()
                p1visibletime, p1visibledata = p1visible.strip().split(':')
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
                bgmtime, bgmdata = bgm.strip().split(':')
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
                         difficulty, wavs, bmps, p1visibles, bgms, lnobj)


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
    column_list = get_keys()
    return column_list


def bgm_divide(chart, time_per_measure, total_time):
    event_list = []
    for measure_counter, measure in enumerate(chart.bgms):
        if measure:
            for lane in measure:
                max_division = len(lane) // 2
                for i in range(0, max_division):
                    note_time = int(measure_counter * time_per_measure + time_per_measure / max_division * i)
                    if lane[0 + i * 2:2 + i * 2] != "00" and lane[0 + i * 2:2 + i * 2] != chart.lnobj:
                        new = 1
                        for j, event in enumerate(event_list):
                            if event[0] == note_time:
                                new = 0
                                break
                        if new == 1:
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
                    note_time = int(measure_counter * time_per_measure + time_per_measure / max_division * i)
                    if lane[0 + i * 2:2 + i * 2] != "00" and lane[0 + i * 2:2 + i * 2] != chart.lnobj:
                        new = 1
                        for j, event in enumerate(event_list):
                            if event[0] == note_time:
                                new = 0
                                break
                        if new == 1:
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


def draw_notes(window, screen, note_positions, judgements):
    for column, note_position in enumerate(note_positions):
        if note_position:
            for index, note in enumerate(note_position):
                if note and "rect" in note:
                    if (column + 1 == 2 or column + 1 == 4 or column + 1 == 6 or column + 1 == 8):
                        pygame.draw.rect(screen, "white", note["rect"])
                    elif (column + 1 == 3 or column + 1 == 5 or column + 1 == 7):
                        pygame.draw.rect(screen, "blue", note["rect"])
                    elif column + 1 == 1:
                        pygame.draw.rect(screen, "red", note["rect"])
                    note_positions[column][index]["rect"] = note["rect"].move(0, 2)
                    if not window.contains(note["rect"]):
                        del note_positions[column][index]["rect"]
                        judgements["miss"] += 1

    pygame.display.flip()


def add_notes(column, window, note_positions, sound, note_time):
    # 8 is the number of columns.
    new_note = pygame.Rect(window[2] / 8 * (LANE_ORDER[column] - 1), 0, 200, 100)
    note_positions[LANE_ORDER[column]-1].append({"rect": new_note, "sound": sound, "time": note_time})
    return note_positions[LANE_ORDER[column]-1]


def update(screen, bgm_list, p1visible_list, current_time, window, note_positions):
    screen.fill(BLACK)
    for i, p1visible_event in enumerate(p1visible_list[0:9]):
        if p1visible_event[0] < current_time + 1000000000:
            for key, sound in p1visible_event[1].items():
                note_positions[LANE_ORDER[key]-1] = add_notes(key, window, note_positions, sound, current_time + 200000000)
            del p1visible_list[i]
    for i, bgm_event in enumerate(bgm_list[0:9]):
        if bgm_event[0] < current_time:
            for sound in bgm_event[1]:
                sound.play()
            del bgm_list[i]
    return note_positions


def play_notes(column_list, p1visible_list, note_positions, current_time, window, judgements, ignore_list):
    keysound_to_play = None
    for column in column_list:
        if note_positions[column-1] and (column not in ignore_list):
            for index, note in enumerate(note_positions[column-1]):
                if note["time"] - HIT_WINDOW < current_time:
                    keysound_to_play = {"sound": note["sound"], "time": note["time"]}
                    del note_positions[column-1][0:index]
                else:
                    break
            if keysound_to_play is not None:
                for index, note in enumerate(note_positions[column-1]):
                    if note["time"] > keysound_to_play["time"]:
                        note_positions[column-1].insert(index, keysound_to_play)
                        del note_positions[column-1][index-1]
                        break
                keysound_to_play["sound"].play()
                if column not in ignore_list:
                    ignore_list.append(column)
                if -10000000 < keysound_to_play["time"] - current_time < 10000000:
                    judgements["great"] += 1
                if -20000000 < keysound_to_play["time"] - current_time < 20000000:
                    judgements["bad"] += 1
            print(note_positions[column-1])
    return ignore_list, note_positions


def gameplay(window, screen, bgm_list, p1visible_list):
    note_positions = [[], [], [], [], [], [], [], []]
    start = time.perf_counter_ns()
    judgements = {"great": 0, "bad": 0, "miss": 0}
    ignore_list = []
    while True:
        note_positions = update(screen, bgm_list, p1visible_list, time.perf_counter_ns() - start, window, note_positions)
        draw_notes(window, screen, note_positions, judgements)
        column_list = keycheck_gameplay()
        if column_list is not None:
            for column in ignore_list:
                if column not in column_list:
                    ignore_list.remove(column)
            ignore_list, note_positions = play_notes(column_list, p1visible_list, note_positions, time.perf_counter_ns() - start, window, judgements, ignore_list)


def main():
    """The main function of the program"""
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
    pygame.mixer.set_num_channels(100)
    chart = parse(PATH + "\\J219.bms")
    bgm_list, p1visible_list, total_time = divide(chart)
    pygame.init()
    # screen size
    screen = pygame.display.set_mode((1920, 1080), DOUBLEBUF | HWSURFACE, depth=8)
    pygame.event.set_allowed([KEYDOWN, KEYUP, QUIT])
    screen.set_alpha(None)
    window = screen.get_rect()
    gameplay(window, screen, bgm_list, p1visible_list)


if __name__ == "__main__":
    main()
