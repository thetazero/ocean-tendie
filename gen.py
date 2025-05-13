from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import csv
import random
import math


DOUBLE_BACKSLASH = "\\\\"
BACKSLASH = "\\"
NEWLINE = "\n"


class Team(Enum):
    ONE = "Gary"
    TWO = "Tim"


class EventKind(Enum):
    TRACK = "Track"
    FIELD = "Field"
    RELAY = "Relay"
    FIELD_RELAY = "Field Relay"

    def is_run(self) -> bool:
        return self in (EventKind.TRACK, EventKind.RELAY)


@dataclass
class Athlete:
    name: str
    team: Team


@dataclass
class EventDef:
    name: str
    duration: int  # In minutes
    entries: list[Athlete]
    kind: EventKind
    max_heat_size: int
    average: float
    std_dev: float


@dataclass
class Event:
    name: str
    time: str
    heats: list[list[tuple[Athlete, str]]]
    kind: EventKind
    average: float
    std_dev: float


def gen_event_list(events: list[Event]) -> str:
    return f"""\\section*{{Event List}}

\\begin{{tabular}}{{@{{}}lllll@{{}}}}
\\toprule
\\textbf{{Event \\#}} & \\textbf{{Event Name}} &  \\textbf{{Time}} \\\\
\\midrule
{
    (NEWLINE).join(
        f"{i + 1} & {event.name} & {event.time} {DOUBLE_BACKSLASH}"
        for i, event in enumerate(events)
    )
}
\\bottomrule
\\end{{tabular}}
"""


def format_seed_time(seed_time: float, average: float) -> str:
    if average < 60:
        return f"{seed_time:.2f}"
    truncated_seconds = math.floor(seed_time % 60 * 10) / 10
    return f"{int(seed_time // 60)}:{truncated_seconds:04.1f}"


def render_heat(
    heat: list[tuple[Athlete, str]], heat_number: int | None, event: Event
) -> str:
    if heat_number is not None:
        return (NEWLINE).join(
            f"{heat_number if i==0 else ''} & {i + 1} & {athlete.name} & {athlete.team.value} & {seed} &{DOUBLE_BACKSLASH}"
            for i, (athlete, seed) in enumerate(heat)
        )
    else:
        return (NEWLINE).join(
            f"{i + 1} & {athlete.name} & {athlete.team.value} & {seed} &{DOUBLE_BACKSLASH}"
            for i, (athlete, seed) in enumerate(heat)
        )


def render_event_heat(event: Event) -> str:
    return f"""
\\textbf{{Event:}} {event.name} \\quad \\textbf{{Time:}} {event.time} 

\\vspace{{1em}}
\\begin{{tabular}}{{@{{}}{"lllll" if len(event.heats) == 1 else "llllll"}@{{}}}}
\\toprule
{
    BACKSLASH + "textbf{{Heat}} &" if len(event.heats) > 1 else ""
}
\\textbf{{{
    'Lane' if event.kind == EventKind.TRACK else 'Order'
}}} & \\textbf{{Athlete Name}} & \\textbf{{Team}} & \\textbf{{{
    'Seed' if event.kind in (EventKind.TRACK, EventKind.RELAY) else 'Mark'
}}} \\\\
\\midrule
{
    (NEWLINE).join(
        render_heat(heat, i + 1 if len(event.heats) > 1 else None, event)
        for i, heat in enumerate(event.heats)
    )
}
\\bottomrule
\\end{{tabular}}
\\vspace{{2.5em}}
"""


def make_heats(
    entries: list[Athlete], max_heat_size: int, avg: float, std_dev: float, is_run: bool
) -> list[list[tuple[Athlete, str]]]:
    random.shuffle(entries)
    heats: list[list[tuple[Athlete, str]]] = []
    times = [max(0, random.gauss(avg, std_dev)) for _ in range(len(entries))]
    if is_run:
        times.sort()
    else:
        times.sort(reverse=True)
    for i in range(0, len(entries), max_heat_size):
        heat: list[tuple[Athlete, str]] = []
        for j in range(i, min(i + max_heat_size, len(entries))):
            mark = times.pop(0)
            if is_run:
                mark = format_seed_time(mark, avg)
            else:
                mark = f"{mark:.2f}"
            heat.append((entries[j], mark))
        heats.append(heat)
    return heats


def generate_heat_sheet(
    name: str,
    date: str,
    location: str,
    host: str,
    description: str,
    meet_history: str,  # New parameter for meet history
    events: list[EventDef],
    start_time: datetime,
    between_event_time: timedelta,
) -> str:
    proc_events: list[Event] = []
    for event in events:
        time_delta = timedelta(minutes=event.duration)
        proc_events.append(
            Event(
                name=event.name,
                time=start_time.strftime("%-I:%M %p"),
                kind=event.kind,
                heats=make_heats(
                    event.entries,
                    event.max_heat_size,
                    event.average,
                    event.std_dev,
                    event.kind.is_run(),
                ),
                average=event.average,
                std_dev=event.std_dev,
            )
        )
        start_time += time_delta + between_event_time

    team_dict = {Team.ONE: set(), Team.TWO: set()}
    for event in proc_events:
        for heat in event.heats:
            for athlete, _ in heat:
                team_dict[athlete.team].add(athlete.name)

    return f"""\\documentclass[10pt]{{article}}
\\usepackage[margin=0.5in]{{geometry}}
\\usepackage{{booktabs}}
\\usepackage{{multicol}}
\\usepackage{{titlesec}}
\\usepackage{{enumitem}}

\\titleformat{{\\section}}{{\\large\\bfseries}}{{}}{{0em}}{{}}
\\titleformat{{\\subsection}}{{\\normalsize\\bfseries}}{{}}{{0em}}{{}}

\\setlist[itemize]{{noitemsep, topsep=0pt}}
\\setlength{{\\parindent}}{{0pt}}

\\begin{{document}}

\\begin{{center}}
    \\LARGE \\textbf{{{name}}} \\\\
    \\large
    \\vspace{{0.5em}}
    \\textbf{{Date:}} {date} \\hspace{{2cm}} \\textbf{{Location:}} {location} \\\\
    \\textbf{{Host:}} {host}
\\end{{center}}

\\vspace{{1em}}

\\section*{{Meet Information}}
{description}

\\vspace{{1em}}

\\section*{{Meet History}}
{meet_history}

\\vspace{{1em}}

{gen_event_list(proc_events)}

\\vspace{{2em}}
\\section*{{Teams}}

{
    (NEWLINE+DOUBLE_BACKSLASH).join(
        f"{BACKSLASH}textbf{{{team.value}}}: {', '.join(sorted(team_dict[team]))}"
        for team in Team
    )
}

\\twocolumn

{
    (NEWLINE).join(
        render_event_heat(event)
        for event in proc_events
    )
}

\\end{{document}}
"""


def parse_entries(
    file_path: str,
    events: list[EventDef],
    name_map: dict[str, Athlete],
    event_map: dict[str, EventDef],
) -> None:
    entry_map: dict[str, list[Athlete]] = {}

    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            selected_events = row["List of events"].strip().split(",")
            for i in range(len(selected_events)):
                selected_events[i] = selected_events[i].strip().lower()
            athlete_name = row["Name"].strip().lower()
            for event_name in selected_events:
                event = event_map.get(event_name)
                if event:
                    athlete = name_map.get(athlete_name)
                    if athlete:
                        entry_map.setdefault(event.name.lower(), []).append(athlete)
                    else:
                        print(f"Athlete '{athlete_name}' not found in name map.")
                else:
                    print(f"Event '{event_name}' not found in event map.")

        for event in events:
            event_name = event.name.lower()
            if event_name in entry_map:
                event.entries = entry_map[event_name]
            else:
                print(f"No entries found for event '{event_name}'.")
    print("Entries parsed successfully.")


def count_events_per_team(events: list[EventDef]) -> dict[Team, int]:
    team_count = {Team.ONE: 0, Team.TWO: 0}
    for event in events:
        for athlete in event.entries:
            team_count[athlete.team] += 1
    return team_count


if __name__ == "__main__":
    LOSHA = Athlete(name="Aleksei Seletskiy", team=Team.ONE)
    NICO = Athlete(name="Nicolo Fasanelli", team=Team.TWO)
    COYLE = Athlete(name="Matthew Coyle", team=Team.ONE)
    EAMON = Athlete(name="Eamon Brady", team=Team.ONE)
    SEAN = Athlete(name="Sean Dutton", team=Team.TWO)
    MARKOS = Athlete(name="Markos Koukoularis", team=Team.TWO)
    KENJI = Athlete(name="Kenji Tella", team=Team.ONE)
    MIA = Athlete(name="Mia Constantin", team=Team.ONE)
    GREG = Athlete(name="Greg Kossuth", team=Team.TWO)
    SETH = Athlete(name="Seth Williams", team=Team.TWO)
    COLIN = Athlete(name="Colin McLaughlin", team=Team.TWO)
    WILL = Athlete(name="William Rifkin", team=Team.TWO)
    TEAM_GARY = Athlete(name="Team Gary", team=Team.ONE)
    TEAM_TIM = Athlete(name="Team Tim", team=Team.TWO)

    random.seed(0)

    hurdles = EventDef(
        name="100 and 10 Hurdles",
        duration=7,
        entries=[],
        kind=EventKind.TRACK,
        max_heat_size=4,
        average=20,
        std_dev=2,
    )
    blind_walk = EventDef(
        name="Blind Walk",
        duration=7,
        entries=[],
        kind=EventKind.FIELD,
        max_heat_size=8,
        average=30,
        std_dev=5,
    )
    random_400_2000 = EventDef(
        name="Random 400-2000",
        duration=10,
        entries=[],
        kind=EventKind.TRACK,
        max_heat_size=20,
        average=200,
        std_dev=120,
    )
    zach_wheel_throw = EventDef(
        name="Zach's Wheel Throw",
        duration=8,
        entries=[],
        kind=EventKind.FIELD,
        max_heat_size=20,
        average=10,
        std_dev=3,
    )
    frisbee = EventDef(
        name="Frisbee Put",
        duration=15,
        entries=[],
        kind=EventKind.FIELD,
        max_heat_size=20,
        average=3,
        std_dev=1,
    )
    shot_relay = EventDef(
        name="Shot Relay",
        duration=11,
        entries=[],
        kind=EventKind.FIELD_RELAY,
        max_heat_size=20,
        average=12,
        std_dev=4,
    )
    hundred_relay = EventDef(
        name="100m Relay",
        duration=5,
        entries=[],
        kind=EventKind.RELAY,
        max_heat_size=9,
        average=18,
        std_dev=2,
    )
    quad_jump = EventDef(
        name="Quadruple Jump",
        duration=12,
        entries=[],
        kind=EventKind.FIELD,
        max_heat_size=20,
        average=14,
        std_dev=3,
    )
    boot_100m = EventDef(
        name="Boot 100m",
        duration=5,
        entries=[],
        kind=EventKind.TRACK,
        max_heat_size=8,
        average=40,
        std_dev=5,
    )
    k_std_dev = EventDef(
        name="1k Std Dev",
        duration=8,
        entries=[],
        kind=EventKind.TRACK,
        max_heat_size=8,
        average=3,
        std_dev=0.5,
    )
    events = [
        k_std_dev,
        boot_100m,
        zach_wheel_throw,
        frisbee,
        shot_relay,
        quad_jump,
        blind_walk,
        hurdles,
        hundred_relay,
        random_400_2000,
    ]
    parse_entries(
        "source.csv",
        events,
        {
            "losha": LOSHA,
            "greg": GREG,
            "mia": MIA,
            "seth": SETH,
            "will": WILL,
            "matthew coyle": COYLE,
            "eamon": EAMON,
            "markos": MARKOS,
            "nicolo fasanelli": NICO,
            "sean": SEAN,
            "coolin": COLIN,
            "kenji tella": KENJI,
            "team gary": TEAM_GARY,
            "team tim": TEAM_TIM,
        },
        {
            "100 and 10 hurdles": hurdles,
            "blind walk": blind_walk,
            "random 400-2000": random_400_2000,
            "wheel throw": zach_wheel_throw,
            "frisbee put": frisbee,
            "frisbee shotput": frisbee,
            "shot relay": shot_relay,
            "shotput relay": shot_relay,
            "100m relay": hundred_relay,
            "quadruple jump": quad_jump,
            "boot 100m": boot_100m,
            "1k standard deviation": k_std_dev,
            "1k std dev": k_std_dev,
        },
    )
    with open("heat_sheet.tex", "w") as f:
        f.write(
            generate_heat_sheet(
                name="Sean Dutton Memorial Ocean Tendie Invitational",
                date="May 13, 2025",
                location="Gesling Stadium",
                host="Carnegie Mellon University",
                description="""This prestigious event honors the legacy of Sean Dutton, featuring a variety of prestigious track and field competitions. Competitors will face challenging events like the Blind Walk, Frisbee Put, and the notorious 100 and 10 Hurdles. May the most ocean tendie team win!
            
\\textbf{Special Rules:}
\\begin{itemize}
  \\item All times and measurements are final, no protests will be accepted
  \\item Team Gary and Team Tim will be awarded points based on a scoring system akin to the Obelisk scoring system
  \\item Boot 100m competitors must provide their own boots
  \\item stdDev competitors must maintain a minimum pace of 5:00/km
\\end{itemize}
""",
                meet_history="""The Sean Dutton Memorial Ocean Tendie Invitational began in 2022 as a friendly competition between Track Club members. What started as a joke quickly evolved into an annual tradition with increasingly bizarre events and scoring methods along with grand slam style prize winnings funded solely by Aleksei Seletskiy. For more info on the history of the event, please visit the [Sean Dutton Memorial Ocean Tendie Invitational Wikipedia page].

\\vspace{0.5em}
\\textbf{Past Champions:}
\\begin{itemize}
  \\item 2022: Team Gary (Captain: Elijah Sech) - 420 points
  \\item 2023: Team Tim (Captain: Sean Dutton) - 420 points
  \\item 2024: Team Gary (Captain: Leland Davies) - 420 points
\\end{itemize}

\\vspace{0.5em}
\\textbf{Notable Records:}
\\begin{itemize}
  \\item Blind Walk: Markos Koukoularis (2023) - Walked 30m without deviating more than 1m from the center line
  \\item Boot 100m: Seth Williams (2024) - 32.56s wearing size 19 Ivanov boots
  \\item Frisbee Put: Coolin Mclaughlin (2022) - 18.7m throw using only his non-dominant hand
\\end{itemize}
""",
                events=events,
                start_time=datetime.strptime("2025-05-13 18:00", "%Y-%m-%d %H:%M"),
                between_event_time=timedelta(minutes=3),
            )
        )
    print("Heat sheet template generated as heat_sheet.tex")
    print(count_events_per_team(events))
