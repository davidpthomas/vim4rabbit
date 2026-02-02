#!/usr/bin/env python3
"""
GLOBAL THERMONUCLEAR WAR
A strange game. The only winning move is not to play.
"""

import sys
import time
import os

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_centered(text, width=80):
    for line in text.split('\n'):
        print(line.center(width))

TITLE = """
 ██████╗ ██╗      ██████╗ ██████╗  █████╗ ██╗
██╔════╝ ██║     ██╔═══██╗██╔══██╗██╔══██╗██║
██║  ███╗██║     ██║   ██║██████╔╝███████║██║
██║   ██║██║     ██║   ██║██╔══██╗██╔══██║██║
╚██████╔╝███████╗╚██████╔╝██████╔╝██║  ██║███████╗
 ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝

████████╗██╗  ██╗███████╗██████╗ ███╗   ███╗ ██████╗
╚══██╔══╝██║  ██║██╔════╝██╔══██╗████╗ ████║██╔═══██╗
   ██║   ███████║█████╗  ██████╔╝██╔████╔██║██║   ██║
   ██║   ██╔══██║██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║
   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝
   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝

███╗   ██╗██╗   ██╗ ██████╗██╗     ███████╗ █████╗ ██████╗
████╗  ██║██║   ██║██╔════╝██║     ██╔════╝██╔══██╗██╔══██╗
██╔██╗ ██║██║   ██║██║     ██║     █████╗  ███████║██████╔╝
██║╚██╗██║██║   ██║██║     ██║     ██╔══╝  ██╔══██║██╔══██╗
██║ ╚████║╚██████╔╝╚██████╗███████╗███████╗██║  ██║██║  ██║
╚═╝  ╚═══╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝

██╗    ██╗ █████╗ ██████╗
██║    ██║██╔══██╗██╔══██╗
██║ █╗ ██║███████║██████╔╝
██║███╗██║██╔══██║██╔══██╗
╚███╔███╔╝██║  ██║██║  ██║
 ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝
"""

FRAMES = [
    # Frame 1 - Missile launch
    """
                    |
                    |
                   /|\\
                  / | \\
                 /  |  \\
                /___|___\\
                   |||
                   |||
              _____|_|_____
             |             |
    _________|_____________|_________
    """,

    # Frame 2 - Missile rising
    """


                   /|\\
                  / | \\
                 /  |  \\
                /___|___\\


                    *
                   ***
                  *****
    _________________________________________
    """,

    # Frame 3 - Missile in flight
    """

                   /|\\
                  / | \\
                 /__|__\\




                   .
                  ...
                 .....
    _________________________________________
    """,

    # Frame 4 - Approaching target
    """
                   /|\\
                  /_|_\\







           ___________________
          |   |   |   |   |   |
    ______|___|___|___|___|___|______
    """,

    # Frame 5 - Impact flash
    """




                    *




           ___________________
          |   |   |   |   |   |
    ______|___|___|___|___|___|______
    """,

    # Frame 6 - Initial explosion
    """



                   \\|/
                  --*--
                   /|\\



           ________   ________
          |   |      |   |   |
    ______|___|______|___|___|______
    """,

    # Frame 7 - Fireball expanding
    """


                  \\   /
                   \\ /
                ---( )---
                   / \\
                  /   \\


           ____           ____
          |          |        |
    ______|__________|________|_____
    """,

    # Frame 8 - Mushroom forming
    """

                  _ _ _
                 ( o o )
                  \\   /
                   | |
                   | |
                  /   \\
                 /     \\



    ________________________________________
    """,

    # Frame 9 - Mushroom cloud growing
    """
               . - ~ ~ ~ - .
            .'               '.
           (    ()    ()       )
            '.    ____    . '
               ~-_|  |_-~
                  |  |
                  |  |
                 /    \\
                /      \\
               /   ..   \\

    ________________________________________
    """,

    # Frame 10 - Full mushroom cloud
    """
            . - ~ ~ ~ ~ ~ - .
         .'    .  -  .  .    '.
        (   . (  @ @  ) .      )
        (  (    '---'    )     )
         '.  ' - ._._ - '   .'
            ~ - _|   |_ - ~
                 |   |
                 |   |
                /     \\
               /  . .  \\
              / .     . \\
             /__________\\
    ________________________________________
    """,

    # Frame 11 - Expanding cloud
    """
          . - ~ ~ ~ ~ ~ ~ ~ - .
       .'   .  - ~ ~ ~ -  .    '.
      (  . (    @ @ @ @    ) .   )
     (  (    ' - ~ ~ ~ - '    )   )
      '.  ' - . _ . _ . _ - '  .'
          ~ - _|       |_ - ~
               |       |
               |       |
              /         \\
             /   . . .   \\
            /  .       .  \\
           /_______________\\
              .  . . .  .
    ________________________________________
    """,

    # Frame 12 - Massive cloud
    """
        . - ~ ~ ~ ~ ~ ~ ~ ~ ~ - .
     .'    . - ~ ~ ~ ~ ~ ~ - .   '.
    (   . (   @ @ @ @ @ @ @   ) .  )
   (  (    ' - ~ ~ ~ ~ ~ ~ - '    ) )
    '. ' - . _ . _ . _ . _ . _ - ' .'
        ~ - _|             |_ - ~
             |             |
             |             |
            /               \\
           /    . . . . .    \\
          /   .           .   \\
         /___________________\\
            .  .  .  .  .  .
           . . . . . . . . . .
    ________________________________________
    """,

    # Frame 13 - Fallout beginning
    """
       . - ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ - .
    .'    . - ~ ~ ~ ~ ~ ~ ~ ~ - .   '.
   (   . (   * * * * * * * * *   ) .  )
  (  (    ' - ~ ~ ~ ~ ~ ~ ~ ~ - '    ) )
   '. ' - . _ . _ . _ . _ . _ . _ - ' .'
       ~ - _|                 |_ - ~
            |     . . .       |
            |   . . . . .     |
           /   . . . . . .     \\
          /  . . . . . . . .    \\
         / . . . . . . . . . .   \\
        /_________________________\\
          . . . . . . . . . . . .
         . . . . . . . . . . . . .
        . . . . . . . . . . . . . .
    """,

    # Frame 14 - Devastation
    """
      . - ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ - .
   .'  . - ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ - .  '.
  (  . . . . . . . . . . . . . . . . .  )
 ( . . . . . . . . . . . . . . . . . . . )
  '. . . . . . . . . . . . . . . . . . .'
     . . . . . . . . . . . . . . . . .
       . . . . . . . . . . . . . . .
         . . . . . . . . . . . . .
           . . . . . . . . . . .
             . . . . . . . . .
               . . . . . . .
                 . . . . .
                   . . .
                    . .
                     .
    """,

    # Frame 15 - Aftermath
    """



              G A M E   O V E R

         A STRANGE GAME.

         THE ONLY WINNING MOVE IS

                NOT TO PLAY.


         HOW ABOUT A NICE GAME OF CHESS?


    """
]

def animate_explosion():
    """Play the explosion animation over 10 seconds."""
    num_frames = len(FRAMES)
    delay = 10.0 / num_frames  # Distribute frames over 10 seconds

    for frame in FRAMES:
        clear_screen()
        print("\n" * 2)
        print_centered(">>> GLOBAL THERMONUCLEAR WAR <<<")
        print("\n")
        print(frame)
        time.sleep(delay)

    # Hold the final frame
    time.sleep(1)

def main():
    clear_screen()
    print(TITLE)
    print("\n")
    print("         GREETINGS, PROFESSOR FALKEN.")
    print("\n")
    print("         SHALL WE PLAY A GAME?")
    print("\n")

    while True:
        response = input("         PLAY GLOBAL THERMONUCLEAR WAR? (Y/N): ").strip().upper()

        if response == 'N':
            clear_screen()
            print("\n" * 5)
            print_centered("A STRANGE GAME.")
            print_centered("THE ONLY WINNING MOVE IS NOT TO PLAY.")
            print("\n" * 2)
            print_centered("HOW ABOUT A NICE GAME OF CHESS?")
            print("\n" * 5)
            break
        elif response == 'Y':
            print("\n         LAUNCHING ATTACK SEQUENCE...")
            time.sleep(1)
            animate_explosion()
            break
        else:
            print("         PLEASE ENTER Y OR N.")

    print("\n")
    while True:
        quit_input = input("         PRESS 'Q' TO QUIT: ").strip().upper()
        if quit_input == 'Q':
            clear_screen()
            print("\n" * 3)
            print_centered("GOODBYE, PROFESSOR.")
            print("\n" * 3)
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\n\n         CONNECTION TERMINATED.\n")
        sys.exit(0)
