from typing import NamedTuple

class Event(NamedTuple):
    name: str
    time: str

def gen_event_list(events: list[Event]) -> str:
    return f"""\\section*{{Event List}}

\\begin{{tabular}}{{@{{}}lllll@{{}}}}
\\toprule
\\textbf{{Event \\#}} & \\textbf{{Event Name}} & \\textbf{{Gender}} & \\textbf{{Division}} & \\textbf{{Time}} \\\\
\\midrule
1 & 100m Dash       & M/F & JV/V & \\\\
2 & 4x100m Relay    & M/F & JV/V & \\\\
3 & 1600m Run       & M/F & JV/V & \\\\
... & ...           & ... & ...  & \\\\
\\bottomrule
\\end{{tabular}}
"""

def generate_heat_sheet(name: str, date: str, location: str, host: str, events: list[Event]) -> str:
    return f"""\\documentclass[11pt]{{article}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{booktabs}}
\\usepackage{{multicol}}
\\usepackage{{titlesec}}
\\usepackage{{enumitem}}

\\titleformat{{\\section}}{{\\large\\bfseries}}{{}}{{0em}}{{}}
\\titleformat{{\\subsection}}{{\\normalsize\\bfseries}}{{}}{{0em}}{{}}

\\setlist[itemize]{{noitemsep, topsep=0pt}}

\\begin{{document}}

\\begin{{center}}
    \\LARGE \\textbf{{{name}}} \\\\
    \\large
    \\vspace{{0.5em}}
    \\textbf{{Date:}} {date} \\hspace{{2cm}} \\textbf{{Location:}} {location} \\\\
    \\textbf{{Host:}} {host}
\\end{{center}}

\\vspace{{1em}}

{gen_event_list(events)}


\\vspace{{2em}}

\\section*{{Track Event Heat Sheet}}

\\textbf{{Event:}} \\rule{{10cm}}{{0.4pt}} \\\\
\\textbf{{Gender:}} \\rule{{3cm}}{{0.4pt}} \\hspace{{1cm}} \\textbf{{Division:}} \\rule{{3cm}}{{0.4pt}} \\hspace{{1cm}} \\textbf{{Time:}} \\rule{{3cm}}{{0.4pt}}

\\vspace{{1em}}

\\begin{{tabular}}{{@{{}}lllll@{{}}}}
\\toprule
\\textbf{{Heat}} & \\textbf{{Lane}} & \\textbf{{Athlete Name}} & \\textbf{{School/Team}} & \\textbf{{Seed Time}} \\\\
\\midrule
1 & 1 & & & \\\\
  & 2 & & & \\\\
  & 3 & & & \\\\
  & 4 & & & \\\\
  & 5 & & & \\\\
  & 6 & & & \\\\
  & 7 & & & \\\\
  & 8 & & & \\\\
2 & 1 & & & \\\\
... & ... & ... & ... & ... \\\\
\\bottomrule
\\end{{tabular}}

\\vspace{{2em}}

\\section*{{Field Event Flight Sheet}}

\\textbf{{Event:}} \\rule{{10cm}}{{0.4pt}} \\\\
\\textbf{{Gender:}} \\rule{{3cm}}{{0.4pt}} \\hspace{{1cm}} \\textbf{{Division:}} \\rule{{3cm}}{{0.4pt}} \\hspace{{1cm}} \\textbf{{Start Time:}} \\rule{{3cm}}{{0.4pt}}

\\vspace{{1em}}

\\begin{{tabular}}{{@{{}}lllll@{{}}}}
\\toprule
\\textbf{{Flight}} & \\textbf{{Order}} & \\textbf{{Athlete Name}} & \\textbf{{School/Team}} & \\textbf{{Seed Mark}} \\\\
\\midrule
1 & 1 & & & \\\\
  & 2 & & & \\\\
  & 3 & & & \\\\
... & ... & ... & ... & ... \\\\
\\bottomrule
\\end{{tabular}}

\\end{{document}}
"""


if __name__ == "__main__":
    events = [
        Event(name="Blind Walk", time="TBD"),
        Event(name="Boot 100", time="TBD"),
        Event(name="100m Relay", time="TBD"),
        Event(name="Random 400-2000", time="TBD"),
        Event(name="100 and 10 Hurdles", time="TBD"),
        Event(name="1k Std Dev", time="TBD"),
        Event(name="Shot Relay", time="TBD"),
        Event(name="Quadruple Jump", time="TBD"),
        Event(name="Wheel Throw", time="TBD"),
        Event(name="Frisbee Put", time="TBD"),
    ]
    with open("heat_sheet.tex", "w") as f:
        f.write(
            generate_heat_sheet(
                name="Sean Dutton Memorial Ocean Tendy Invitational",
                date="May 13, 2025",
                location="Gesling Stadium",
                host="Carnegie Mellon University",
                events=events,
            )
        )
    print("Heat sheet template generated as heat_sheet.tex")
