import pygame
import sys
import re
import array
import time
import simpleaudio as sa
import os

BLACK = (0, 0, 0)
DESIRED_DT = 8000000

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

    with open(file, 'r') as file_object:
        line = file_object.readline()
        p1visiblemax = bgmmax = 1

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
                wavs[wavindex] = sa.WaveObject.from_wave_file(PATH + wavfile)

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


def divide(chart):
    meter = 4
    end = max(len(chart.bgms), len(chart.p1visibles))
    # amount of desired dts per measure
    indices = int(
        (1 / (chart.bpm * meter) * 60 * 1000000000) * end // DESIRED_DT)
    event_list = [None] * indices
    indices_per_measure = indices // len(chart.p1visibles)
    measure_counter = 0
    note_index = 0
    # To do: Convert time events to lists!!!!!
    for measure in chart.p1visibles:
        for j, lane in measure.items():
            max_division = len(lane) // 2
            for i in range(0, max_division):
                note_index = int(measure_counter * indices_per_measure + \
                                 indices_per_measure / max_division * i)
                if lane[0 + i * 2:2 + i * 2] != "00" and lane[
                                                         0 + i * 2:2 + i * 2] != chart.lnobj:
                    event_list[note_index] = chart.wavs[
                        lane[0 + i * 2:2 + i * 2]]
                    print(note_index)
        measure_counter += 1
    print(event_list)


def update(dt, screen):
    screen.fill(BLACK)
    keycheck_gameplay()
    pygame.display.flip()


def gameplay(window, screen):
    dt = DESIRED_DT
    while True:
        start = time.perf_counter_ns()
        update(dt, screen)
        elapsed_dt = time.perf_counter_ns() - start
        if elapsed_dt < DESIRED_DT:
            pygame.time.wait(elapsed_dt // 1000000 + 1)
            dt = DESIRED_DT
        else:
            dt = elapsed_dt - DESIRED_DT
            if dt > DESIRED_DT * 10:
                dt = DESIRED_DT * 10


def main():
    """The main function of the program"""
    chart = parse(PATH + "ajisaiN.bms")
    divide(chart)
    pygame.init()
    # screen size
    screen = pygame.display.set_mode((1920, 1080))
    window = screen.get_rect()
    while True:
        gameplay(window, screen)


if __name__ == "__main__":
    main()
