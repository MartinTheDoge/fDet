import json
import sqlite3
import ast
from bs4 import BeautifulSoup

class HOVER:
    def __init__(self, tokenizer=None, type="train") -> None:
        self.tokenizer = tokenizer
        if type == "train":
            self.file = []
            with open(r"datasets/HoVer/my_train.jsonl", "r") as f:
                for line in f:
                    self.file.append(json.loads(line))
        elif type == "test":
            self.file = []
            with open(r"datasets/HoVer/my_test.jsonl", "r") as f:
                for line in f:
                    self.file.append(json.loads(line))
            
    def __len__(self):
        return len(self.file)

    def extractEvidence(self, evidenceList, err) -> str:
            evidence = ""
            # Evidence extract
            for i in evidenceList:
                title = i[0]
                sentence = i[1] + 1
                if title == None:
                    return evidence, err
                # Wiki page extract
                dbfile = r"datasets\HoVer\db_wiki\hover_wiki.db"
                con = sqlite3.connect(dbfile)
                cur = con.cursor()
                try:
                    data = cur.execute('SELECT text FROM wiki WHERE title = "{}" '.format(title)).fetchone()
                except sqlite3.OperationalError:
                    data = cur.execute("SELECT text FROM wiki WHERE title = '{}' ".format(title)).fetchone()
                if data == None:
                    err += 1
                    return evidence, err
                data = ast.literal_eval(data[0])
                dataList = []
                for i in data:
                    dataList += i
                try: 
                    soup = BeautifulSoup(dataList[sentence], 'html.parser')
                    text = soup.get_text()
                    evidence += f"{text} \n"
                except: evidence += f""
            # Get evidence
            try: con.close()
            except: pass
            return evidence, err

    def generate_dataset(self) -> list:
        newFile = []
        err = 0
        for i in self.file:
            evidenceList = i["supporting_facts"]
            evidence, err = self.extractEvidence(evidenceList, err)
            label = i["label"]
            if label == "SUPPORTED": label = 0
            elif label == "NOT_SUPPORTED": label = 1
            newFile.append({"uid": i["uid"] , "claim": i["claim"], "evidence": evidence, "label": label})
        return newFile

    def __getitem__(self, idx):
        evidence = self.file[idx]["evidence"]
        claim = self.file[idx]["claim"]
        label = self.file[idx]["label"]
        batch = self.tokenizer.encode_plus(claim, evidence, truncation="longest_first" , max_length=512, padding="max_length", return_tensors="pt")                                     
        return batch, label

# file = json.load(open(r"datasets\HoVer\hover_train_release_v1.1.json", "r"))

# file[0]
# print("END")
# file = json.load(open(r"datasets\HoVer\hover_dev_release_v1.1.json", "r"))



# file = json.load(open(r"datasets\HoVer\hover_train_release_v1.1.json", "r"))
# file = json.load(open(r"datasets\HoVer\hover_dev_release_v1.1.json", "r"))


# def count(file):
#     sup, ref = 0, 0
#     for i in file:
#         if i["label"] == "SUPPORTED": sup += 1
#         elif i["label"] == "NOT_SUPPORTED": ref += 1
#     return sup, ref

# s,r = count(file=file)
# print(f"{s}\n{r}")