import json

def analyze(path):
    SUP,REF,NEI = 0, 0, 0
    testFile = []
    with open(path, 'r', encoding="utf-8") as f:
        for line in f:
            testFile.append(json.loads(line))
    for j, i in enumerate(testFile):
        if i["label"] == "SUPPORTS" or i["label"] == 0 :
            SUP += 1
        elif i["label"] == "REFUTES" or i["label"] == 1:
            REF += 1
        elif i["label"] == "NOT ENOUGH INFO" or i["label"] == 2:
            NEI += 1
    print(f"Support {SUP}\nRefutes {REF}\nNot enough info {NEI}")

def divide(path, out_file):
    SUP,REF,NEI = 0,0,0
    testFile = []
    with open(path, 'r',  encoding="utf-8") as f:
        for line in f:
            testFile.append(json.loads(line))
    for j, i in enumerate(testFile):
        if i["label"] == 0 and SUP < 7148:
            json.dump(i, out_file)
            out_file.write("\n")
            SUP += 1
        if i["label"] == 1 and REF < 7148:
            json.dump(i, out_file)
            out_file.write("\n")
            REF += 1
        if i["label"] == 2:
            json.dump(i, out_file)
            out_file.write("\n")
            NEI += 1
    print(f"Support {SUP}\nRefutes {REF}\nNot enough info {NEI}")

def merge(path1, path2):
    SUP,REF,NEI = 0,0,0
    supportsFile = []
    refutesFile = []
    fn = 0
    outputFile = open(f"my_file{fn}.jsonl", "w")
    with open(path1, 'r') as f:
        for line in f:
            supportsFile.append(json.loads(line))
    with open(path2, 'r') as f:
        for line in f:
            refutesFile.append(json.loads(line))
    n = 0
    for i in range(len(supportsFile)):
        json.dump(supportsFile[i], outputFile)
        outputFile.write("\n")
        json.dump(refutesFile[n], outputFile)
        n += 1
        outputFile.write("\n")
        if n >= 7148:
            n = 0
            outputFile.close()
            fn += 1
            outputFile = open(f"my_train{fn}.jsonl", "w")

def countLen(path):
    File = []
    with open(path, 'r') as f:
        for line in f:
            File.append(json.loads(line))
    print(len(File))


def combine(file1, file2):
    import random
    newFile = file1 + file2
    random.shuffle(newFile)
    return newFile


