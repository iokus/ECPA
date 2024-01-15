# run to parse all eve data files within directory

import re
from os import listdir, path, mkdir
from argparse import ArgumentParser
from evelyzer import analyze


class Entry:
    def __init__(self, time: str, effect: float, target: str, role: str) -> None:
        self.time = time
        self.effect = effect
        self.target = target
        self.role = role

    def __str__(self) -> str:
        return f"{self.role},{self.time},{self.effect},{self.target}"


def getSegment(segments: list, timestamp: str) -> int:
    timeInt = timestampToInt(timestamp)
    res = -1
    for i in range(len(segments)):
        if timeInt >= timestampToInt(segments[i][0]):
            if timeInt <= timestampToInt(segments[i][1]):
                res = i
                break
    return res


def readFile(fi: str, segments: list) -> list:
    entries = list()
    with open(fi, "r") as log:
        for line in log:
            if line[0] != "[":
                continue
            if (getSegment(segments, line.split(" ")[2]) == -1) or any(
                _ in line
                for _ in (
                    "Vizan's Modified Mega",
                    "Warp scramble attempt",
                    "Large Vorton Projector II",
                    "Chelm's Modified",
                )
            ):
                continue

            if ("combat" in line) and any(
                _ in line
                for _ in (
                    "Hits",
                    "Smashes",
                    "Grazes",
                    "Penetrates",
                    "Glances",
                    "Wrecks",
                )
            ):
                try:
                    effect = re.search(">[0-9]+<", line).group().strip("><")

                    target = (
                        re.search(
                            "\\(([^\\)]+)\\)", line.split("combat")[1]
                        )  # will fuck things up if someone has a name in ()
                        .group()
                        .strip("()")
                    )
                    if "from" in line:
                        role = "dps-received"
                    else:
                        role = "dps-to"
                    entries.append(Entry(line.split(" ")[2], effect, target, role))
                except Exception as e:
                    print(line + ":", end=" ")
                    print(e.args)
                    # print(buffer[9])
                    break

            if ("combat" in line) and (
                ("shield boosted" in line) or ("armor repaired" in line)
            ):  # add armor
                effect = re.search(">[0-9]+<", line).group().strip("><")

                buffer = re.findall(">[\w\[\]\(\) ]+<", line)

                if len(buffer) > 1:
                    if "> remote shield boosted to <" in buffer:
                        buffer.remove("> remote shield boosted to <")

                    if "> remote shield boosted by <" in buffer:
                        buffer.remove("> remote shield boosted by <")

                    if "> remote armor repaired to <" in buffer:
                        buffer.remove("> remote armor repaired to <")

                    if "> remote armor repaired by <" in buffer:
                        buffer.remove("> remote armor repaired by <")
                else:
                    continue

                if (
                    "remote shield boosted by" in line
                    or "remote armor repaired by" in line
                ):
                    role = "logi-received"
                else:
                    role = "logi-to"

                if len(buffer) < 2:
                    continue

                entries.append(
                    Entry(
                        line.split(" ")[2],
                        buffer[0].strip("><"),
                        buffer[1].strip("><"),
                        role,
                    )
                )

            if ("combat" in line) and (
                "energy neutralized" in line
            ):  # fix target, <color=0xfff0f000> unique
                if "<color=0xffe57f7f>" in line:
                    role = "got-neuted"
                    target = re.search("\\(([^\\)]+)\\)", line.split("combat")[1])
                    if target == None:
                        target = "enemy"
                    else:
                        target = target.group().strip("()")
                else:
                    role = "neuted-enemy"
                    try:
                        if re.search("\\([\w ]+\\)", line.split("combat")[1]) == None:
                            target = "enemy"
                        else:
                            target = (
                                re.search(
                                    "\\([\w ]+\\)", line.split("combat")[1]
                                )  # will fuck things up if someone has a name in ()
                                .group()
                                .strip("()")
                            )
                    except:
                        print(line)
                        exit(1)
                effect = re.search("[0-9]+ GJ", line).group().split(" ")[0]
                entries.append(
                    Entry(
                        line.split(" ")[2],
                        effect,
                        target,
                        role,
                    )
                )

            if ("combat" in line) and ("energy drained to" in line):
                role = "got-drained"
                target = (
                    re.search(
                        "\\(([^\\)]+)\\)", line.split("combat")[1]
                    )  # will fuck things up if someone has a name in ()
                    .group()
                    .strip("()")
                )
                effect = re.search("[0-9]+ GJ", line).group().split(" ")[0]
                entries.append(
                    Entry(
                        line.split(" ")[2],
                        effect,
                        target,
                        role,
                    )
                )

            if ("combat" in line) and ("energy drained from" in line):
                role = "drained-enemy"

                target = re.search("\\(([^\\)]+)\\)", line.split("combat")[1])
                if target != None:
                    target = target.group().strip("()")
                else:
                    target = "enemy"
                effect = re.search("[0-9]+ GJ", line).group().split(" ")[0]
                entries.append(
                    Entry(
                        line.split(" ")[2],
                        effect,
                        target,
                        role,
                    )
                )

    return entries


def timestampToInt(timestamp: str) -> int:
    tmp = timestamp.split(":")
    return int(tmp[0]) * 3600 + int(tmp[1]) * 60 + int(tmp[2])


# --------------------------------------------------script start--------------------------------------#
parser = ArgumentParser(
    prog="A program for analysing EVE combat log files",
    description="A program for analysing EVE combat log files and compa ring comp perfermance",
)
parser.add_argument(
    "-d",
    "--dir",
    required=True,
    help="a path to a directory in which log files are present, may be relative to script location or absolute",
)
parser.add_argument(
    "-t",
    "--time",
    required=True,
    help="a time of log segments which you want to analyse separately (could be sets, matches...) format in evetime: {HH:MM:SS-HH:MM:SS,HH:MM:SS-HH:MM:SS...}",
)

args = parser.parse_args()
tmp = str(args.time).split(",")
segments = []
seglist = []
for seg in tmp:
    segments.append(seg.split("-"))
    seglist.append(seg)
    if not path.isdir(args.dir + "/" + seg):
        mkdir(args.dir + "/" + seg)

# ---------------------------------------------------main logic ----------------------------------------#
for fi in listdir(args.dir):
    if ".txt" in fi:
        print("parsing: " + fi)
        # write to file setup
        entries = readFile(fi, segments)
        iteration = 0
        data = iter(entries)
        tmp = next(data, None)
        if not tmp:
            exit(0)

        lastSegment = getSegment(segments, tmp.time)
        if not path.isfile(
            f"{args.dir}/{seglist[lastSegment]}/{fi.split('.')[0].split('-')[iteration]}.csv"
        ):
            out = open(
                f"{args.dir}/{seglist[lastSegment]}/{fi.split('.')[0].split('-')[iteration]}.csv",
                "w",
            )
        else:
            for i in range(2, 5):
                if not path.isfile(
                    f"{args.dir}/{seglist[lastSegment]}/{fi.split('.')[0].split('-')[iteration]}-{i}.csv"
                ):
                    out = open(
                        f"{args.dir}/{seglist[lastSegment]}/{fi.split('.')[0].split('-')[iteration]}-{i}.csv",
                        "w",
                    )
                    break
        out.write("type,time,amount,target\n")

        out.write(str(tmp) + "\n")
        tmp = next(data, None)

        # writing loop

        while tmp is not None:
            # print(f"segment is {lastSegment}")
            if lastSegment != getSegment(segments, tmp.time):
                lastSegment = getSegment(segments, tmp.time)

                if iteration < len(fi.split(".")[0].split("-")) - 1:
                    iteration += 1
                    out.close()

                    if not path.isfile(
                        f"{args.dir}/{seglist[lastSegment]}/{fi.split('.')[0].split('-')[iteration]}.csv"
                    ):
                        out = open(
                            f"{args.dir}/{seglist[lastSegment]}/{fi.split('.')[0].split('-')[iteration]}.csv",
                            "w",
                        )
                    else:
                        for i in range(2, 5):
                            if not path.isfile(
                                f"{args.dir}/{seglist[lastSegment]}/{fi.split('.')[0].split('-')[iteration]}-{i}.csv"
                            ):
                                out = open(
                                    f"{args.dir}/{seglist[lastSegment]}/{fi.split('.')[0].split('-')[iteration]}-{i}.csv",
                                    "w",
                                )
                                break
                out.write("type,time,amount,target\n")
            out.write(str(tmp) + "\n")
            tmp = next(data, None)

        out.close()

for s in seglist:
    analyze(s)
