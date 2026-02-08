"""
Global Thermonuclear War - Based on the 1983 movie WarGames (V4R-52).

Enter password 'joshua' to access WOPR. Press 'x' to launch missiles.
AI responds with counter-launches. After 3 rounds the classic ending plays.
"""

import random
from typing import List


PASSWORD = "joshua"
MAX_LAUNCHES = 3

COUNTRIES = [
    "UNITED STATES", "SOVIET UNION", "UNITED KINGDOM", "FRANCE",
    "CHINA", "INDIA", "JAPAN", "WEST GERMANY", "AUSTRALIA", "BRAZIL",
    "CANADA", "IRAN", "NORTH KOREA", "EGYPT", "ISRAEL",
]

GLOBE = [
    "               _.--\"\"\"--.._",
    "            .'  N. AMERICA  '.",
    "           /    .---. EUROPE  \\",
    "          |    |     |  ASIA   |",
    "          |     '---'          |",
    "          |    AFRICA     .--. |",
    "           \\  S. AMERICA |AU| /",
    "            '.           '--'.'",
    "              ''--.....--''",
]


class WarGames:
    """Global Thermonuclear War - inspired by the 1983 film."""

    def __init__(self, width: int, height: int) -> None:
        self.width = max(width, 50)
        self.height = max(height - 4, 16)
        self._game_over = False

        # Password phase
        self.phase = "password"
        self.typed = ""
        self.pw_error = False

        # War phase
        self.human_targets: List[str] = []
        self.ai_targets: List[str] = []
        self.launches = 0
        self._pool = list(COUNTRIES)
        random.shuffle(self._pool)

        # Missile animation
        self._anim_ticks = 0
        self._anim_who = ""  # "human" or "ai"

    def tick(self) -> None:
        """Advance one frame."""
        if self._game_over or self.phase in ("password", "globe"):
            return

        if self.phase == "missile":
            self._anim_ticks += 1
            if self._anim_ticks >= 5:
                if self._anim_who == "human":
                    # Human animation done - AI fires back
                    self._fire_ai()
                    self._anim_who = "ai"
                    self._anim_ticks = 0
                else:
                    # AI animation done
                    if self.launches >= MAX_LAUNCHES:
                        self._game_over = True
                    else:
                        self.phase = "globe"

    def _fire_ai(self) -> None:
        """AI launches at a random country."""
        if self._pool:
            target = self._pool.pop()
        else:
            target = random.choice(COUNTRIES)
        self.ai_targets.append(target)

    def handle_input(self, key: str) -> None:
        """Process a keypress."""
        if self._game_over:
            if key == "o" and self.phase != "great_choice":
                self.phase = "great_choice"
            return

        if self.phase == "password":
            if len(key) == 1 and key.isalpha():
                self.typed += key.lower()
                self.pw_error = False
                if len(self.typed) >= len(PASSWORD):
                    if self.typed == PASSWORD:
                        self.phase = "globe"
                    else:
                        self.pw_error = True
                        self.typed = ""

        elif self.phase == "globe" and key == "x":
            if self.launches < MAX_LAUNCHES and self._pool:
                target = self._pool.pop()
                self.human_targets.append(target)
                self.launches += 1
                self.phase = "missile"
                self._anim_ticks = 0
                self._anim_who = "human"

    def get_frame(self) -> List[str]:
        """Return the current display."""
        if self.phase == "password":
            return self._frame_password()
        elif self.phase == "missile":
            return self._frame_missile()
        return self._frame_globe()

    def _frame_password(self) -> List[str]:
        """WOPR password entry screen."""
        lines: List[str] = []
        cy = max((self.height - 14) // 2, 0)
        for _ in range(cy):
            lines.append("")

        prompt = self.typed + "_" * (len(PASSWORD) - len(self.typed))
        if self.pw_error:
            msg = "IDENTIFICATION NOT RECOGNIZED."
        else:
            msg = "ENTER PASSWORD TO CONTINUE..."

        lines.append("   ╔═════════════════════════════════════════╗")
        lines.append("   ║                                         ║")
        lines.append("   ║   GREETINGS PROFESSOR FALKEN.           ║")
        lines.append("   ║                                         ║")
        lines.append("   ║   SHALL WE PLAY A GAME?                 ║")
        lines.append("   ║                                         ║")
        lines.append(f"   ║   PASSWORD: [ {prompt:<6} ]                  ║")
        lines.append("   ║                                         ║")
        lines.append(f"   ║   {msg:<37}  ║")
        lines.append("   ║                                         ║")
        lines.append("   ║                                         ║")
        lines.append("   ╚═════════════════════════════════════════╝")
        lines.append("")
        lines.append("  WarGames  |  Type password  |  [c] cancel")

        return lines

    def _frame_globe(self) -> List[str]:
        """Main war room display with globe and launch log."""
        lines: List[str] = []
        lines.append("")
        lines.append("   ══════════ W.O.P.R. ══════════")
        lines.append("   GLOBAL THERMONUCLEAR WAR")
        lines.append(f"   DEFCON: {max(5 - self.launches, 1)}")
        lines.append("")

        for row in GLOBE:
            lines.append("   " + row)
        lines.append("")

        for i, t in enumerate(self.human_targets):
            lines.append(f"   YOU  >> MISSILE #{i + 1} -> {t}")
        for i, t in enumerate(self.ai_targets):
            lines.append(f"   WOPR >> MISSILE #{i + 1} -> {t}")
        if self.human_targets or self.ai_targets:
            lines.append("")

        remaining = MAX_LAUNCHES - self.launches
        lines.append(f"   [x] LAUNCH ({remaining} remaining)")
        lines.append("")
        lines.append("  WarGames  |  [c] cancel")

        return lines

    def _frame_missile(self) -> List[str]:
        """Missile in-flight animation."""
        lines: List[str] = []
        lines.append("")
        lines.append("   ══════════ W.O.P.R. ══════════")
        lines.append("   GLOBAL THERMONUCLEAR WAR")
        lines.append(f"   DEFCON: {max(5 - self.launches, 1)}")
        lines.append("")

        if self._anim_who == "human":
            target = self.human_targets[-1]
            label = "YOU"
        else:
            target = self.ai_targets[-1]
            label = "WOPR"

        trail = "=" * min(self._anim_ticks * 4, 20)
        warhead = ">" if self._anim_ticks < 4 else "*"

        lines.append(f"   {label} LAUNCHING AT: {target}")
        lines.append("")
        lines.append(f"   [{trail}{warhead}]")
        lines.append("")

        for row in GLOBE:
            lines.append("   " + row)
        lines.append("")

        for i, t in enumerate(self.human_targets):
            lines.append(f"   YOU  >> MISSILE #{i + 1} -> {t}")
        for i, t in enumerate(self.ai_targets):
            lines.append(f"   WOPR >> MISSILE #{i + 1} -> {t}")
        lines.append("")
        lines.append("  WarGames  |  [c] cancel")

        return lines

    def is_game_over(self) -> bool:
        """Check end state."""
        return self._game_over

    def get_game_over_frame(self) -> List[str]:
        """The iconic WarGames ending."""
        if self.phase == "great_choice":
            return self._frame_great_choice()

        lines: List[str] = []
        lines.append("")
        lines.append("")
        cy = max((self.height - 16) // 2, 0)
        for _ in range(cy):
            lines.append("")

        lines.append("        ╔═══════════════════════════════════════╗")
        lines.append("        ║                                       ║")
        lines.append("        ║        * * * GAME OVER * * *          ║")
        lines.append("        ║                                       ║")
        lines.append("        ║            WINNER: NONE               ║")
        lines.append("        ║                                       ║")
        lines.append("        ║          A STRANGE GAME.              ║")
        lines.append("        ║       THE ONLY WINNING MOVE IS        ║")
        lines.append("        ║            NOT TO PLAY.               ║")
        lines.append("        ║                                       ║")
        lines.append("        ║    HOW ABOUT A NICE GAME OF CHESS?    ║")
        lines.append("        ║                                       ║")
        lines.append("        ║        [o] OK. Good decision.         ║")
        lines.append("        ║                                       ║")
        lines.append("        ╚═══════════════════════════════════════╝")
        lines.append("")
        lines.append("  WarGames  |  [o] OK  |  [c] cancel")

        return lines

    def _frame_great_choice(self) -> List[str]:
        """Big bold 'Great Choice!' screen."""
        lines: List[str] = []
        cy = max((self.height - 12) // 2, 0)
        for _ in range(cy):
            lines.append("")

        lines.append("    ╔══════════════════════════════════════════════════╗")
        lines.append("    ║                                                  ║")
        lines.append("    ║    ██████ ██████ ██████  █████ ████████ ██       ║")
        lines.append("    ║   ██      ██   █ ██     ██   ██   ██   ██       ║")
        lines.append("    ║   ██  ██  █████  ████   ███████   ██   ██       ║")
        lines.append("    ║   ██   █  ██  █  ██     ██   ██   ██            ║")
        lines.append("    ║    █████  ██  ██ ██████ ██   ██   ██   ██       ║")
        lines.append("    ║                                                  ║")
        lines.append("    ║    █████ ██  ██  █████  ██  █████ ██████ ██     ║")
        lines.append("    ║   ██     ██  ██ ██   ██ ██ ██     ██     ██     ║")
        lines.append("    ║   ██     ██████ ██   ██ ██ ██     ████          ║")
        lines.append("    ║   ██     ██  ██ ██   ██ ██ ██     ██            ║")
        lines.append("    ║    █████ ██  ██  █████  ██  █████ ██████ ██     ║")
        lines.append("    ║                                                  ║")
        lines.append("    ║                                                  ║")
        lines.append("    ╚══════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("  WarGames  |  [c] cancel")

        return lines
