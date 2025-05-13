from typing import NamedTuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import csv


DOUBLE_BACKSLASH = "\\\\"
BACKSLASH = "\\"
NEWLINE = "\n"


class Team(Enum):
    ONE = "Carnegie University of Melon"
    TWO = "Melon University of Carnegie"


class EventKind(Enum):
    TRACK = "Track"
    FIELD = "Field"
    RELAY = "Relay"
    FIELD_RELAY = "Field Relay"


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


@dataclass
class Event:
    name: str
    time: str
    heats: list[list[Athlete]]
    kind: EventKind


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


def render_heat(heat: list[Athlete], heat_number: int | None) -> str:
    if heat_number is not None:
        return (NEWLINE).join(
            f"{heat_number if i==0 else ''} & {i + 1} & {athlete.name} & {athlete.team.value} & seed time &{DOUBLE_BACKSLASH}"
            for i, athlete in enumerate(heat)
        )
    else:
        return (NEWLINE).join(
            f"{i + 1} & {athlete.name} & {athlete.team.value} & seed time &{DOUBLE_BACKSLASH}"
            for i, athlete in enumerate(heat)
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
}}} & \\textbf{{Athlete Name}} & \\textbf{{School/Team}} & \\textbf{{Seed Time}} \\\\
\\midrule
{
    (NEWLINE).join(
        render_heat(heat, i + 1 if len(event.heats) > 1 else None)
        for i, heat in enumerate(event.heats)
    )
}
\\bottomrule
\\end{{tabular}}
\\vspace{{2.5em}}
"""


def make_heats(entries: list[Athlete], max_heat_size: int) -> list[list[Athlete]]:
    heats = []
    for i in range(0, len(entries), max_heat_size):
        heats.append(entries[i : i + max_heat_size])
    return heats


def generate_heat_sheet(
    name: str,
    date: str,
    location: str,
    host: str,
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
                heats=make_heats(event.entries, event.max_heat_size),
            )
        )
        start_time += time_delta + between_event_time

    return f"""\\documentclass[11pt]{{article}}
\\usepackage[margin=1in]{{geometry}}
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

{gen_event_list(proc_events)}


\\vspace{{2em}}

\\section*{{Track Event Heat Sheet}}

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


if __name__ == "__main__":
    LOSHA = Athlete(name="Aleksei Seletskiy", team=Team.ONE)
    NICO = Athlete(name="Nicolo Fasanelli", team=Team.ONE)
    COYLE = Athlete(name="Matthew Coyle", team=Team.ONE)
    EAMON = Athlete(name="Eamon Brady", team=Team.ONE)
    SEAN = Athlete(name="Sean Dutton", team=Team.ONE)
    MARKOS = Athlete(name="Markos Koukoularis", team=Team.ONE)
    KENJI = Athlete(name="Kenji Tella", team=Team.TWO)
    MIA = Athlete(name="Mia Constantin", team=Team.TWO)
    GREG = Athlete(name="Greg Kossuth", team=Team.TWO)
    SETH = Athlete(name="Seth Williams", team=Team.TWO)
    COLIN = Athlete(name="Colin McLaughlin", team=Team.TWO)
    WILL = Athlete(name="William Rifkin", team=Team.TWO)

    events = [
        EventDef(
            name="100 and 10 Hurdles",
            duration=7,
            entries=[],
            kind=EventKind.TRACK,
            max_heat_size=4,
        ),
        EventDef(
            name="Blind Walk",
            duration=7,
            entries=[],
            kind=EventKind.TRACK,
            max_heat_size=8,
        ),
        EventDef(
            name="Random 400-2000",
            duration=10,
            entries=[],
            kind=EventKind.TRACK,
            max_heat_size=20,
        ),
        EventDef(
            name="Zach's Wheel Throw",
            duration=8,
            entries=[],
            kind=EventKind.FIELD,
            max_heat_size=20,
        ),
        EventDef(
            name="Frisbee Put",
            duration=15,
            entries=[],
            kind=EventKind.FIELD,
            max_heat_size=20,
        ),
        EventDef(
            name="Shot Relay",
            duration=9,
            entries=[],
            kind=EventKind.FIELD_RELAY,
            max_heat_size=20,
        ),
        EventDef(
            name="100m Relay",
            duration=5,
            entries=[],
            kind=EventKind.RELAY,
            max_heat_size=8,
        ),
        EventDef(
            name="Quadruple Jump",
            duration=12,
            entries=[],
            kind=EventKind.FIELD,
            max_heat_size=20,
        ),
        EventDef(
            name="Boot 100m",
            duration=5,
            entries=[],
            kind=EventKind.TRACK,
            max_heat_size=8,
        ),
        EventDef(
            name="1k Std Dev",
            duration=8,
            entries=[],
            kind=EventKind.TRACK,
            max_heat_size=8,
        ),
    ]
    parse_entries(
        "source.csv",
        events,
        {
            "losha": LOSHA,
            "greg": GREG,
            "kenji": KENJI,
            "mia": MIA,
            "seth": SETH,
            "will": WILL,
            "matthew coyle": COYLE,
            "eamon": EAMON,
            "markos": MARKOS,
            "nicol": NICO,
            "sean": SEAN,
            "coolin": COLIN,
        },
        {
            "100 and 10 hurdles": events[0],
            "blind walk": events[1],
            "random 400-2000": events[2],
            "wheel throw": events[3],
            "frisbee put": events[4],
            "frisbee shotput": events[4],
            "shot relay": events[5],
            "shotput relay": events[5],
            "100m relay": events[6],
            "quadruple jump": events[7],
            "boot 100m": events[8],
            "1k standard deviation": events[9],
            "1k std dev": events[9],
        },
    )
    with open("heat_sheet.tex", "w") as f:
        f.write(
            generate_heat_sheet(
                name="Sean Dutton Memorial Ocean Tendie Invitational",
                date="May 13, 2025",
                location="Gesling Stadium",
                host="Carnegie Mellon University",
                events=events,
                start_time=datetime.strptime("2025-05-13 18:00", "%Y-%m-%d %H:%M"),
                between_event_time=timedelta(minutes=3),
            )
        )
    print("Heat sheet template generated as heat_sheet.tex")
