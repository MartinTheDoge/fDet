import json
import re
import sqlite3
from torch.utils.data import Dataset

class FEVEROUS(Dataset):
    def __init__(self, tokenizer=None, type="train0"):
        self.tokenizer = tokenizer
        if type.lower() == "train0":
            self.file = []
            with open(r"datasets/FEVER/feverous/my_train0.jsonl", 'r', encoding="utf8") as f:
                for line in f:
                    self.file.append(json.loads(line))
        elif type.lower() == "train1":
            self.file = []
            with open(r"datasets/FEVER/feverous/my_train1.jsonl", 'r', encoding="utf8") as f:
                for line in f:
                    self.file.append(json.loads(line))
        elif type.lower() == "num":
            self.file = []
            with open(r"datasets/FEVER/feverous/my_num_feverous.jsonl", 'r', encoding="utf8") as f:
                for line in f:
                    self.file.append(json.loads(line))
        elif type.lower() == "test":
            self.file = []
            with open(r"datasets/FEVER/feverous/my_test.jsonl", 'r', encoding="utf8") as f:
                for line in f:
                    self.file.append(json.loads(line))
            
    def __len__(self) -> int:
        return len(self.file)

    def extractEvidence(self, evidenceList):
        # Evidence extract
        evidence = ""
        for content in evidenceList:
            for id in content["content"]:
                title, item = re.split("_", id, 1)
                numbers = re.findall(r"\d+", item)
                # Wiki page extract
                dbfile = r"datasets\FEVER\db_wiki\feverous_wikiv1.db"
                con = sqlite3.connect(dbfile)
                cur = con.cursor()
                data = cur.execute('SELECT data FROM wiki WHERE id = "{}" '.format(title)).fetchone()
                dataJson = json.loads(data[0])
                # Sentence
                if re.search(".+_sentence", id):
                    Path = item
                    evidence += f"{dataJson[Path]} "
                # Cell
                elif re.search(".+_cell", id):
                    Path = f"table_{numbers[0]}"
                    data = dataJson[Path]["table"]
                    for row in data:
                        for info in row:
                            if info["id"] == item:
                                evidence += f"{info['value']} "
                # Header cell
                elif re.search(".+_header_cell", id):
                    Path = f"table_{numbers[0]}"
                    data = dataJson[Path][0]["table"]
                    for row in data:
                        for info in row:
                            if info["id"] == item:
                                evidence += f"{info['value']} "
                # Table caption
                elif re.search(".+_table_caption", id):
                    Path = f"table_{numbers[0]}"
                    evidence += f"{dataJson[Path]['caption']} "
                # Item
                elif re.search(".+_item", id):
                    Path = f"list_{numbers[0]}"
                    data = dataJson[Path]["list"]
                    for row in data:
                         if row["id"] == item:
                            # evidence += f"{row["value]}\n"
                            evidence += f"{row['value']} "
            evidence += "\n"
        try: con.close()
        except: pass
        # Final formating to string for model
        return evidence
        
    def __getitem__(self, idx):
        claim = self.file[idx]["claim"]
        label = self.file[idx]["label"]
        evidence = self.file[idx]["evidence"]
        batch = self.tokenizer.encode_plus(claim, evidence, truncation="longest_first", max_length=512, padding="max_length", return_tensors="pt")                                     
        return batch, label

    def getRow(self, idx):
        claim = self.file[idx]["claim"]
        label = self.file[idx]["label"]
        evidence = self.file[idx]["evidence"]
        return claim, label, evidence

    def FeverousGen(self, file, max, min = 0):
        tempFile = []
        with open(file, 'r') as f:
            for line in f:
                tempFile.append(json.loads(line))
        Myfile = []
        Done = 0
        for idx in range(min, max + 1):
            if Done % 2000 == 0:
                log = f"{(Done/len(file)):>5f}% : [{Done:>5f}/{len(file):>5f}]\n"
                print(log)
                
            label = file[idx]['label']
            if (label == "SUPPORTS"):           label = 0
            elif (label == "REFUTES"):          label = 1
            elif (label == "NOT ENOUGH INFO"):  label = 2

            if (len(file[idx]["evidence"]) > 1):
                for row in range(len(file[idx]["evidence"])):
                    FileRow = {'id': file[idx]['id'], 'claim': file[idx]['claim'], 'label': label,
                               'evidence': file[idx]['evidence'][row]}
                    Myfile.loc[len(Myfile.index)] = FileRow
                    Done += 1
                continue
            FileRow = {'id': file[idx]['id'], 'claim': file[idx]['claim'], 'label': label,
                       'evidence': file[idx]['evidence'][0]}
            Myfile.dump(FileRow)
            json.dump()
            Done += 1
        return Myfile

    def FeverGenWiki(self, file, min, max):
        MyFile = []
        Done = 0
        for idx in range(min, max):
            if Done % 2000 == 0:
                log = f"{(Done/max):>2f}% : [{min+Done:>1f}/{max:>1f}]\n"
                print(log)

            label = file[idx]['label']
            if (label == "SUPPORTS"):     
                label = 0 
            elif (label == "REFUTES"):      
                label = 1
            elif (label == "NOT ENOUGH INFO"):  
                label = 2

            evidence = self.extractEvidence(file[idx]["evidence"])
            if evidence != "":
                FileRow = {'id': int(file[idx]['id']), 'claim': file[idx]['claim'], 'label': label, 'evidence': evidence}
                MyFile.append(FileRow)
                Done += 1
        return MyFile
