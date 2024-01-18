import csv
from os import listdir, path


def analyze(path: str):
    matches = listdir(path)
    for match in matches:
        with open(f"{path}/{match}/summary.csv", "w") as summary:
            summary.write(
                "ship,damage dealt,damage received,logi received,logi dealt, neuted enemy, got neuted, drained enemy, got drained\n"
            )

            sumDmgD = 0
            sumDmgR = 0
            sumLD = 0
            sumLR = 0
            sumNR = 0
            sumND = 0
            sumDR = 0
            sumDD = 0

            for fi in listdir(f"{path}/{match}"):
                if fi == "summary.csv":
                    continue
                with open(f"{path}/{match}/{fi}", newline="") as csvfile:
                    print(f"analyzing: {fi}")
                    r = csv.DictReader(csvfile)
                    dpsDealt = 0
                    dpsReceived = 0
                    logiReceived = 0
                    logiDealt = 0
                    gotNeuted = 0
                    neuted = 0
                    gotDrained = 0
                    drained = 0

                    for row in r:
                        # print(row)
                        match row["type"]:
                            case "dps-received":
                                dpsReceived += int(row["amount"])
                            case "dps-to":
                                dpsDealt += int(row["amount"])
                            case "logi-received":
                                logiReceived += int(row["amount"])
                            case "logi-to":
                                logiDealt += int(row["amount"])
                            case "neuted-enemy":
                                neuted += int(row["amount"])
                            case "got-neuted":
                                gotNeuted += int(row["amount"])
                            case "drained-enemy":
                                drained += int(row["amount"])
                            case "got-drained":
                                gotDrained += int(row["amount"])

                    sumDmgD += dpsDealt
                    sumDmgR += dpsReceived
                    sumLD += logiDealt
                    sumLR += logiReceived
                    sumND += neuted
                    sumNR += gotNeuted
                    sumDR += gotDrained
                    sumDD += drained
                    summary.write(
                        f"{fi.split('.')[0]},{dpsDealt},{dpsReceived},{logiReceived},{logiDealt},{neuted},{gotNeuted},{drained},{gotDrained}\n"
                    )

            summary.write(
                f"comp total,{sumDmgD},{sumDmgR},{sumLR},{sumLD},{sumND},{sumNR},{sumDD},{sumDR}\n"
            )


def summarize(p, basefile):
    for f in listdir(p):
        if path.isdir(f"{p}/{f}"):
            summarize(f"{p}/{f}", basefile)
        if path.isfile(f"{p}/{f}"):
            if f == "summary.csv":
                with open(f"{p}/{f}", "r") as infile:
                    basefile.write(f"-------{p}/{f}---------\n")
                    for line in infile:
                        basefile.write(line)
                    basefile.write("\n\n")


def dump(p: str, basefile) -> None:
    for f in listdir(p):
        if path.isdir(f"{p}/{f}"):
            dump(f"{p}/{f}", basefile)
        if path.isfile(f"{p}/{f}") and len(f.split(".")) > 1:
            if f != "summary.csv" and f.split(".")[1] == "csv" and f != "dump.csv":
                with open(f"{p}/{f}", "r") as infile:
                    for line in infile:
                        if line != "type,time,amount,target\n":
                            tmp = line.strip("\n")
                            # print(f"line = {tmp}\np={p}\nf={f.split('.')[0]}")
                            loc = p.split("/")
                            basefile.write(
                                f"{loc[len(loc)-2]},{loc[len(loc)-1].split('-')[1]},{f.split('.')[0]},{tmp}\n"
                            )


with open("dump.csv", "w") as f:
    f.write("set,match,ship,type,time,amount,target\n")
    dump(".", f)
