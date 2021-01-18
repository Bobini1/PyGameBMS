import pygame
import sys
import re
import time
import simpleaudio as sa
import threading
from ctypes import c_buffer, windll
from random import random
from sys import getfilesystemencoding


def winCommand(*command):
    buf = c_buffer(255)
    command = ' '.join(command).encode(getfilesystemencoding())
    int(windll.winmm.mciSendStringA(command, buf, 254, 0))
    return buf.value


def playsoundWin(sound, mode):
    '''
    Utilizes windll.winmm. Tested and known to work with MP3 and WAVE on
    Windows 7 with Python 2.7. Probably works with more file formats.
    Probably works on Windows XP thru Windows 10. Probably works with all
    versions of Python.

    Inspired by (but not copied from) Michael Gundlach <gundlach@gmail.com>'s mp3play:
    https://github.com/michaelgundlach/mp3play

    I never would have tried using windll.winmm without seeing his code.
    '''

    if mode == 'read':
        alias = 'playsound_' + str(random())
        winCommand('open "' + sound + '" alias', alias)
        winCommand('set', alias, 'time format milliseconds')
        return alias
    if mode == 'play':
        durationInMS = winCommand('status', sound, 'length')
        winCommand('play', sound, 'from 0 to', durationInMS.decode())


BLACK = (0, 0, 0)
DESIRED_DT = 2000000
PATH = r"C:\Users\PC\PycharmProjects\PygameBMS\Bird Sprite -D.K.R. mix-"
WHITE_NUMBER = 1000000000


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
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 8,
    "8": 6,
    "9": 7,
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


def g_event(command):
    """
    Function used to run gameplay-specific commands

    :param str command: a gameplay command
    """


def s_event(command):
    """
    Function used to process and play sound events

    :param str command: a sound command
    """
    pass


def v_event(command):
    """
    Function used to process and display bga events

    :param str command: a video command
    """
    pass


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
                # wavs[wavindex] = sa.WaveObject.from_wave_file(PATH + "\\" + wavfile)
                # wavs[wavindex] = SoundLoader.load(PATH + "\\" + wavfile)
                # wavs[wavindex] = pygame.mixer.Sound(PATH + "\\" + wavfile)
                wavs[wavindex] = playsoundWin(PATH + "\\" + wavfile, 'read')

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
                    p1visibles.append(None)
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
                    print(bgmtime)
                    print(bgmmax)
                    bgms.append(None)
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


def array_fill(chart):
    measures = max(len(chart.bgms), len(chart.p1visibles))
    print(chart.p1visibles)


def keycheck_gameplay():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                pass


def bgm_divide(chart, indices_per_measure, indices):
    event_list = [None] * indices
    for measure_counter, measure in enumerate(chart.bgms):
        if measure is not None:
            for lane in measure:
                max_division = len(lane) // 2
                for i in range(0, max_division):
                    note_index = int(measure_counter * indices_per_measure + \
                                     indices_per_measure / max_division * i + WHITE_NUMBER // DESIRED_DT)
                    if lane[0 + i * 2:2 + i * 2] != "00" and lane[0 + i * 2:2 + i * 2] != chart.lnobj:
                        if event_list[note_index] is None:
                            event_list[note_index] = [chart.wavs[lane[0 + i * 2:2 + i * 2]]]
                        else:
                            event_list[note_index].append(chart.wavs[lane[0 + i * 2:2 + i * 2]])
    return event_list


def p1visible_divide(chart, indices_per_measure, indices):
    event_list = [None] * indices
    for measure_counter, measure in enumerate(chart.p1visibles):
        if measure is not None:
            for key, lane in measure.items():
                max_division = len(lane) // 2
                for i in range(0, max_division):
                    note_index = int(measure_counter * indices_per_measure + \
                                     indices_per_measure / max_division * i + WHITE_NUMBER // DESIRED_DT)
                    if lane[0 + i * 2:2 + i * 2] != "00" and lane[0 + i * 2:2 + i * 2] != chart.lnobj:
                        if event_list[note_index] is None:
                            event_list[note_index] = {key: chart.wavs[lane[0 + i * 2:2 + i * 2]]}
                        else:
                            event_list[note_index][key] = (chart.wavs[lane[0 + i * 2:2 + i * 2]])
    return event_list


def divide(chart):
    meter = 4
    end = max(len(chart.bgms), len(chart.p1visibles))
    # amount of desired dts per measure
    indices = int(((meter / chart.bpm * 60 * 1000000000) * end + WHITE_NUMBER) // DESIRED_DT)
    print("indices: " + str(indices))
    indices_per_measure = indices // len(chart.p1visibles)
    indices += WHITE_NUMBER // DESIRED_DT
    p1visible_list = p1visible_divide(chart, indices_per_measure, indices)
    bgm_list = bgm_divide(chart, indices_per_measure, indices)
    return bgm_list, p1visible_list, indices


def draw_notes(init_time, p1visible_list, window, screen, note_positions):
    if p1visible_list[init_time] is not None:
        for lane, key in p1visible_list[init_time].items():
            # 8 is the number of lanes.
            new_note = pygame.Rect(window[2] / 8 * (LANE_ORDER[lane] - 1), 0, 100, 50)
            note_positions.append(new_note)
    for index, note in enumerate(note_positions):
        if note is not None:
            pygame.draw.rect(screen, "blue", note)
            note_positions[index] = note.move(0, 2)
            if not window.contains(note):
                del note_positions[index]


def update(screen, bgm_list, p1visible_list, index, window, note_positions):
    screen.fill(BLACK)
    keycheck_gameplay()
    draw_notes(index + WHITE_NUMBER // DESIRED_DT, p1visible_list, window, screen, note_positions)
    if p1visible_list[index] is not None:
        for key, sound in p1visible_list[index].items():
            if sound is not None:
                playsoundWin(sound, 'play')
    if bgm_list[index] is not None:
        for sound in bgm_list[index]:
            if sound is not None:
                playsoundWin(sound, 'play')
    pygame.display.flip()


def gameplay(window, screen, bgm_list, p1visible_list, chart, indices):
    dt = DESIRED_DT
    note_positions = []
    print(chart.bgms)
    print(chart.p1visibles)
    for index in range(0, indices):
        start = time.perf_counter_ns()
        update(screen, bgm_list, p1visible_list, index, window, note_positions)
        elapsed_dt = time.perf_counter_ns() - start
        if elapsed_dt < DESIRED_DT:
            pygame.time.wait((DESIRED_DT - elapsed_dt) // 1000000)


def main():
    """The main function of the program"""
    chart = parse(PATH + "\\bs_7a.bme")
    bgm_list, p1visible_list, indices = divide(chart)
    pygame.init()
    # screen size
    screen = pygame.display.set_mode((1920, 1080))
    window = screen.get_rect()
    gameplay(window, screen, bgm_list, p1visible_list, chart, indices)


if __name__ == "__main__":
    main()
