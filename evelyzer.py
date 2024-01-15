import csv
from os import listdir


def analyze(path: str):
    with open(f"{path}/summary.csv", "w") as summary:
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

        for fi in listdir(path):
            if fi == "summary.csv":
                continue
            with open(f"{path}/{fi}", newline="") as csvfile:
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
