import csv
from os import listdir


def analyze(path: str):
    with open(f"{path}/summary.csv", "w") as summary:
        summary.write("ship,damage dealt,damage received,logi received,logi dealt\n")

        sumDmgD = 0
        sumDmgR = 0
        sumLD = 0
        sumLR = 0

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

                sumDmgD += dpsDealt
                sumDmgR += dpsReceived
                sumLD += logiDealt
                sumLR += logiReceived
                summary.write(
                    f"{fi.split('.')[0]},{dpsDealt},{dpsReceived},{logiReceived},{logiDealt}\n"
                )

        summary.write(f"comp total,{sumDmgD},{sumDmgR},{sumLR},{sumLD}\n")
