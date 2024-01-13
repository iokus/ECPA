# run to parse all eve data files within directory

import re
from os import listdir, path


class Entry:
    def __init__(self, time: str, effect: float, target: str, role: str) -> None:
        self.time = time
        self.effect = effect
        self.target = target
        self.role = role

    def __str__(self) -> str:
        return f"{self.role},{self.time},{self.effect},{self.target}"


def readFile(fi: str) -> list:
    entries = list()
    with open(fi, "r") as log:
        for line in log:
            if (
                ("combat" in line)
                and any(
                    _ in line
                    for _ in (
                        "Hits",
                        "Smashes",
                        "Grazes",
                        "Penetrates",
                        "Glances",
                        "Wrecks",
                    )
                )
                and not ("Vizan's Modified Mega") in line
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
    return entries


for fi in listdir():
    if ".txt" in fi:
        print("parsing: " + fi)
        # write to file setup
        entries = readFile(fi)
        data = iter(entries)
        tmp = next(data, None)
        if not tmp:
            exit(0)

        lastTime: int = int(
            int(tmp.time.split(":")[1]) + int(tmp.time.split(":")[0]) * 60
        )
        iteration = 0

        if not path.isfile(f"{fi.split('.')[0].split('-')[iteration]}.csv"):
            out = open(f"{fi.split('.')[0].split('-')[iteration]}.csv", "w")
        else:
            for i in range(2, 5):
                if not path.isfile(f"{fi.split('.')[0].split('-')[iteration]}-{i}.csv"):
                    out = open(f"{fi.split('.')[0].split('-')[iteration]}-{i}.csv", "w")
                    break

        out.write(str(tmp) + "\n")
        tmp = next(data, None)

        # writing loop
        while tmp is not None:
            if (
                abs(
                    int(
                        int(tmp.time.split(":")[1])
                        + int(tmp.time.split(":")[0]) * 60
                        - lastTime
                    )
                )
                > 9
            ) and (iteration < len(fi.split(".")[0].split("-")) - 1):
                out.close()
                iteration += 1

                if not path.isfile(f"{fi.split('.')[0].split('-')[iteration]}.csv"):
                    out = open(f"{fi.split('.')[0].split('-')[iteration]}.csv", "w")
                else:
                    for i in range(2, 5):
                        if not path.isfile(
                            f"{fi.split('.')[0].split('-')[iteration]}-{i}.csv"
                        ):
                            out = open(
                                f"{fi.split('.')[0].split('-')[iteration]}-{i}.csv", "w"
                            )
                            break

            out.write(str(tmp) + "\n")
            lastTime = int(
                int(tmp.time.split(":")[1]) + int(tmp.time.split(":")[0]) * 60
            )
            tmp = next(data, None)

        out.close()
