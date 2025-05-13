from typing import NamedTuple
from datetime import datetime, timedelta
from dataclasses import dataclass



DOUBLE_BACKSLASH = "\\\\"
NEWLINE = "\n"

@dataclass
class EventDef:
    name: str
    duration: int # In minutes

@dataclass
class Event:
    name: str
    time: str

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

def render_event_heat(event: Event) -> str:
    return f"""
\\textbf{{Event:}} {event.name} \\quad \\textbf{{Time:}} {event.time} 

\\vspace{{1em}}
\\begin{{tabular}}{{@{{}}lllll@{{}}}}
\\toprule
\\textbf{{Lane}} & \\textbf{{Athlete Name}} & \\textbf{{School/Team}} & \\textbf{{Seed Time}} \\\\
\\midrule
1 & & & \\\\
2 & & & \\\\
3 & & & \\\\
4 & & & \\\\
5 & & & \\\\
6 & & & \\\\
7 & & & \\\\
8 & & & \\\\
\\bottomrule
\\end{{tabular}}
\\vspace{{2.5em}}
"""

def generate_heat_sheet(name: str, date: str, location: str, host: str, events: list[EventDef], start_time: datetime, between_event_time: timedelta) -> str:
    proc_events: list[Event] = []
    for event in events:
        time_delta = timedelta(minutes=event.duration)
        proc_events.append(Event(name=event.name, time=start_time.strftime("%-I:%M %p")))
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


if __name__ == "__main__":
    events = [
        EventDef(name="100 and 10 Hurdles", duration=7),
        EventDef(name="Blind Walk", duration=7),
        EventDef(name="Random 400-2000", duration=10),
        EventDef(name="Wheel Throw", duration=8),
        EventDef(name="Frisbee Put", duration=15),
        EventDef(name="Shot Relay", duration=9),
        EventDef(name="100m Relay", duration=5),
        EventDef(name="Quadruple Jump", duration=12),
        EventDef(name="Boot 100m", duration=5),
        EventDef(name="1k Std Dev", duration=8),
    ]
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
