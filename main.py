import pygame


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
    pass


def main():
    """The main function of the program"""
    pygame.init()
    # screen size
    scr = pygame.display.set_mode((1920, 1080))
    win = scr.get_rect()


if __name__ == "__main__":
    main()
