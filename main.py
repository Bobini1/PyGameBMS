import pygame
import sys
import pandas
import re

BLACK = (0, 0, 0)


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


def parse(file):
    """
    The function used to parse the bms file into internal variables

    Parameters:
    file (string): the path to the file that is to be parsed
    """

    with open(file) as file:
        file_contents = file.read()
        file.close()
        meta = {
            "player": re.compile(r'(?<=#PLAYER )[1-4]($|\n)'),
            "genre": re.compile(r'(?<=#GENRE ).+($|\n)'),
            "title": re.compile(r'(?<=#TITLE ).+($|\n)'),
            "subtitle": re.compile(r'(?<=#SUBTITLE ).+($|\n)'),
            "artist": re.compile(r'(?<=#ARTIST ).+($|\n)'),
            "subartist": re.compile(r'(?<=#SUBARTIST ).+($|\n)'),
            "bpm": re.compile(r'(?<=#BPM )\d+($|\n)'),
            "playlevel": re.compile(r'(?<=#PLAYLEVEL )\d+($|\n)'),
            "total": re.compile(r'(?<=#TOTAL )\d+($|\n)'),
            "volwav": re.compile(r'(?<=#RANK )\d+($|\n)'),
            "stagefile": re.compile(r'(?<=#STAGEFILE ).+($|\n)'),
            "rank": re.compile(r'(?<=#RANK )[0-3]($|\n)'),
            "banner": re.compile(r'(?<=#BANNER ).+($|\n)'),
            "difficulty": re.compile(r'(?<=#DIFFICULTY ).+($|\n)'),
            "wav": re.compile(r'(?<=#WAV)\w\w \d+($|\n)'),
            "defexrank": re.compile(r'(?<=#DEFEXRANK ).+($|\n)'),
            "backbmp": re.compile(r'(?<=#BACKBMP ).+($|\n)'),
            "charfile": re.compile(r'(?<=#CHARFILE ).+($|\n)'),
            "maker": re.compile(r'(?<=#MAKER ).+($|\n)'),
            "textxx": re.compile(r'(?<=#TEXT)\w\w .+($|\n)'),
            "songxx": re.compile(r'(?<=#SONG)\w\w .+($|\n)'),
            "exrankxx": re.compile(r'(?<=#EXRANK)\w\w \d+($|\n)'),
            "bpmxx": re.compile(r'(?<=#BPM)\w\w \d+($|\n)'),
            "exbpmxx": re.compile(r'(?<=#EXBPM)\w\w \d+($|\n)'),
            "stopxx": re.compile(r'(?<=#STOP)\w\w \d+($|\n)'),
            "changeoptionxx": re.compile(r'(?<=#CHANGEOPTION)\w\w .+($|\n)'),
            "exwavxx": re.compile(r'(?<=#EXWAV)\w\w .+($|\n)'),
            "bmpxx": re.compile(r'(?<=#BMP)\w\w .+($|\n)'),
            "exbmpxx": re.compile(r'(?<=#EXBMP)\w\w .+($|\n)'),
            "bgaxx": re.compile(r'(?<=#BGA)\w\w .+($|\n)'),
            "@bgaxx": re.compile(r'(?<=#@BGA)\w\w .+($|\n)'),
            "swbgaxx": re.compile(r'(?<=#SWBGA)\w\w .+($|\n)'),
            "argbxx": re.compile(r'(?<=#ARGB)\w\w .+($|\n)'),
            "seekxx": re.compile(r'(?<=#SEEK)\w\w \d+($|\n)'),
            "stp": re.compile(r'(?<=#STP )\d\d\d\.\d\d\d \d+($|\n)'),
            "landmine": re.compile(r'#\w*[D-E][1-9]:.+($|\n)'),
            "pathwav": re.compile(r'(?<=#PATH_WAV ).+($|\n)'),
            "basebpm": re.compile(r'(?<=#BASEBPM )\d+($|\n)'),
            "lntype": re.compile(r'(?<=#LNTYPE )\d+($|\n)'),
            "lnobj": re.compile(r'(?<=#LNOBJ )\w+($|\n)'),
            "octfp": re.compile(r'#OCT/FP'),
            "option": re.compile(r'(?<=#OPTION ).+($|\n)'),
            "wavcmd": re.compile(r'(?<=#WAVCMD ).+($|\n)'),
            "cdda": re.compile(r'(?<=#CDDA )\d+($|\n)'),
            "midifile": re.compile(r'(?<=#MIDIFILE ).+($|\n)'),
            "poorbga": re.compile(r'(?<=#POORBGA )[0-2]+($|\n)'),
            "videofile": re.compile(r'(?<=#VIDEOFILE ).+($|\n)'),
            "videofs": re.compile(r'(?<=#VIDEOf/s )\d+($|\n)'),
            "videocolors": re.compile(r'(?<=#VIDEOCOLORS ).+($|\n)'),
            "videodly": re.compile(r'(?<=#VIDEODLY )\d+($|\n)'),
            "movie": re.compile(r'(?<=#MOVIE ).+($|\n)'),
            "extchr": re.compile(r'(?<=#ExtChr ).+($|\n)'),
            "materialswav": re.compile(r'(?<=#MATERIALSWAV ).+($|\n)'),
            "materialsbmp": re.compile(r'(?<=#MATERIALSBMP ).+($|\n)'),
            "divideprop": re.compile(r'(?<=#DIVIDEPROP )\d+($|\n)'),
            "charset": re.compile(r'(?<=#CHARSET ).+($|\n)'),
            "url": re.compile(r'(?<=%URL ).+($|\n)'),
            "email": re.compile(r'(?<=%EMAIL ).+($|\n)'),
            "random": re.compile(r'(?<=#RANDOM )\d+($|\n)'),
            "endrandom": re.compile(r'(?<=#ENDRANDOM )\d+($|\n)'),
            "rondam": re.compile(r'(?<=#RONDAM )\d+($|\n)'),
            "if": re.compile(r'(?<=#if )\d+($|\n)'),
            "endif": re.compile(r'#endif($|\n)'),
            "end_if": re.compile(r'#end if($|\n)'),
            "setrandom": re.compile(r'(?<=#SETRANDOM )\d+($|\n)'),
            "elseif": re.compile(r'(?<=#ELSEIF )\d+($|\n)'),
            "else": re.compile(r'#ELSE($|\n)'),
            "switch": re.compile(r'(?<=#SWITCH )\d+($|\n)'),
            "setswitch": re.compile(r'(?<=#SETSWITCH )\d+($|\n)'),
            "case": re.compile(r'(?<=#CASE )\d+($|\n)'),
            "def": re.compile(r'#DEF($|\n)'),
            "skip": re.compile(r'#SKIP($|\n)'),
            "endsw": re.compile(r'#ENDSW($|\n)'),






        }


def keycheck_gameplay():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                pass


def gameplay(window, screen):
    screen.fill(BLACK)
    pygame.display.flip()


def main():
    """The main function of the program"""
    pygame.init()
    # screen size
    screen = pygame.display.set_mode((1920, 1080))
    window = screen.get_rect()
    while True:
        gameplay(window, screen)


if __name__ == "__main__":
    main()
