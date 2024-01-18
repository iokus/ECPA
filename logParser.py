# run to parse all eve data files within directory

import re
from os import listdir, path, mkdir
from argparse import ArgumentParser
from evelyzer import analyze, summarize, dump


class Entry:
    def __init__(self, time: str, effect: float, target: str, role: str) -> None:
        self.time = time
        self.effect = effect
        self.target = target
        self.role = role

    def __str__(self) -> str:
        return f"{self.role},{self.time},{self.effect},{self.target}"


class Segment:
    def __init__(self, sign: str, beginInt: int, endInt: int) -> None:
        self.sign = sign
        self.begin = beginInt
        self.end = endInt

    def __str__(self) -> str:
        return self.sign

    def contains(self, timestamp: str) -> bool:
        if (timestampToInt(timestamp) >= self.begin) and (
            timestampToInt(timestamp) <= self.end
        ):
            return True
        return False


def getSegmentPos(segments: list, timestamp: str) -> int:
    for i in range(len(segments)):
        if segments[i].contains(timestamp):
            return i
    return -1


def getSegment(segments: list, sign: str) -> Segment:
    for s in segments:
        # print(f"looking for {sign} in {s.sign}")
        if s.contains(sign):
            return s
    return None


def readFile(fi: str, segments: list) -> list:
    entries = list()
    with open(fi, "r") as log:
        for line in log:
            if line[0] != "[":
                continue
            if (getSegmentPos(segments, line.split(" ")[2]) == -1) or any(
                _ in line
                for _ in (
                    "Vizan's Modified Mega",
                    "Warp scramble attempt",
                    "Large Vorton Projector II",
                    "Chelm's Modified",
                    "Tournament Bubble",
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
                target = re.search(
                    "\\(([^\\)]+)\\)", line.split("combat")[1]
                )  # will fuck things up if someone has a name in ()
                if target == None:
                    target = "enemy"
                else:
                    target = target.group().strip("()")
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

            if "(None) Undocking" in line:
                entries.append(
                    Entry(
                        line.split(" ")[2],
                        "none",
                        "none",
                        "undock",
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
for seg in tmp:
    segments.append(
        Segment(
            seg, timestampToInt(seg.split("-")[0]), timestampToInt(seg.split("-")[1])
        )
    )
    if not path.isdir(args.dir + "/" + seg):
        mkdir(args.dir + "/" + seg)
        mkdir(f"{args.dir}/{seg}/match-1")

# ---------------------------------------------------main logic ----------------------------------------#
for fi in listdir(args.dir):
    if ".txt" in fi:
        print("parsing: " + fi)
        # write to file setup
        entries = readFile(fi, segments)
        fileSegments = dict()
        for s in segments:
            fileSegments.update({s.sign: []})

        # add entries to corresponding segments
        for e in entries:
            fileSegments[getSegment(segments, e.time).sign].append(e)

        # clean undocks only
        keysToDelete = []
        for s in fileSegments:
            used = False
            for e in fileSegments[s]:
                if e.role != "undock":
                    used = True
                    break
            if not used:
                keysToDelete.append(s)
        for k in keysToDelete:
            del fileSegments[k]

        # write active segments

        iteration = 0
        for k in fileSegments:
            lastUndock = timestampToInt(fileSegments[k][0].time)
            match = 1

            if not path.isfile(
                f"{args.dir}/{k}/match-{match}/{fi.split('.')[0].split('-')[iteration]}.csv"
            ):
                out = open(
                    f"{args.dir}/{k}/match-{match}/{fi.split('.')[0].split('-')[iteration]}.csv",
                    "w",
                )
            else:
                for i in range(2, 5):
                    if not path.isfile(
                        f"{args.dir}/{k}/match-{match}/{fi.split('.')[0].split('-')[iteration]}-{i}.csv"
                    ):
                        out = open(
                            f"{args.dir}/{k}/match-{match}/{fi.split('.')[0].split('-')[iteration]}-{i}.csv",
                            "w",
                        )
                        break

            out.write("type,time,amount,target\n")

            for e in fileSegments[k]:
                if e.role == "undock" and (timestampToInt(e.time) - lastUndock) > 120:
                    lastUndock = timestampToInt(e.time)
                    match += 1

                    if not path.isdir(f"{args.dir}/{k}/match-{match}"):
                        mkdir(f"{args.dir}/{k}/match-{match}")

                    if not path.isfile(
                        f"{args.dir}/{k}/match-{match}/{fi.split('.')[0].split('-')[iteration]}.csv"
                    ):
                        out = open(
                            f"{args.dir}/{k}/match-{match}/{fi.split('.')[0].split('-')[iteration]}.csv",
                            "w",
                        )
                    else:
                        for i in range(2, 5):
                            if not path.isfile(
                                f"{args.dir}/{k}/match-{match}/{fi.split('.')[0].split('-')[iteration]}-{i}.csv"
                            ):
                                out = open(
                                    f"{args.dir}/{k}/match-{match}/{fi.split('.')[0].split('-')[iteration]}-{i}.csv",
                                    "w",
                                )

                                break

                    out.write("type,time,amount,target\n")

                else:
                    out.write(str(e) + "\n")

            iteration += 1


for s in segments:
    analyze(s.sign)

base = open(f"{args.dir}/all.txt", "w")
summarize(args.dir, base)
base.close()

base = open(f"{args.dir}/dump.txt", "w")
dump(args.dir, base)
base.close()
