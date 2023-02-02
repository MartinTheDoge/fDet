import json
import re
import sqlite3
from torch.utils.data import Dataset

class FEVER(Dataset):
        def __init__(self, tokenizer=None, type="train0") -> None:
            self.tokenizer = tokenizer
            if type.lower() == "train0":
                self.file = []
                with open(r"datasets/FEVER/fever1/label/my_train0.jsonl", 'r') as f:
                    for line in f:
                        self.file.append(json.loads(line))
            elif type.lower() == "train1":
                self.file = []
                with open(r"datasets/FEVER/fever1/label/my_train1.jsonl", 'r') as f:
                    for line in f:
                        self.file.append(json.loads(line))
            elif type.lower() == "train2":
                self.file = []
                with open(r"datasets/FEVER/fever1/label/my_train2.jsonl", 'r') as f:
                    for line in f:
                        self.file.append(json.loads(line))
            elif type.lower() == "test":
                self.file = []
                with open(r"datasets/FEVER/fever1/label/my_test.jsonl", 'r') as f:
                    for line in f:
                        self.file.append(json.loads(line))
            elif type.lower() == "val":
                self.file = []
                with open(r"datasets/FEVER/fever1/label/my_val.jsonl", 'r') as f:
                    for line in f:
                        self.file.append(json.loads(line))

        def __len__(self) -> int:
            return len(self.file)

        def extractEvidence(self, evidenceList) -> str:
            evidence = ""
            # Evidence extract
            evidenceContent = []
            for i in evidenceList:
                title = i[2]
                sentence = i[3]
                if title == None:
                    return evidence
                # Wiki page extract
                dbfile = r"Algo\datasets\FEVER\db_wiki\FEVER_wikiv1.db"
                con = sqlite3.connect(dbfile)
                cur = con.cursor()
                try:
                    data = cur.execute('SELECT lines FROM wiki WHERE id = "{}" '.format(title)).fetchone()
                except sqlite3.OperationalError:
                    data = cur.execute("SELECT lines FROM wiki WHERE id = '{}' ".format(title)).fetchone()
                if data == None:
                    return evidence
                dataText = re.findall(f"{sentence}\t.+\n", data[0])[0]
                dataText = re.sub(f"{sentence}\t", "", dataText, 1)
                evidence += f"{dataText}"
            # Get evidence
            try: con.close()
            except: pass
            return evidence


        def __getitem__(self, idx)  -> list:
            evidence = self.file[idx]["evidence"]
            claim = self.file[idx]["claim"]
            label = self.file[idx]["label"]
            batch = self.tokenizer.encode_plus(claim, evidence, truncation="longest_first" , max_length=512, padding="max_length", return_tensors="pt")                                     
            return batch, label

        def FeverGenWiki(self, file, min, max):
            MyFile = []
            Done = 0
            for idx in range(min, max):
                if Done % 2000 == 0:
                    log = f"{(Done/max):>2f}% : [{min+Done:>1f}/{max:>1f}]\n"
                    print(log)

                label = file.iloc[idx]['label']
                if (label == "SUPPORTS"):     
                    label = 0 
                elif (label == "REFUTES"):      
                    label = 1
                elif (label == "NOT ENOUGH INFO"):  
                    label = 2

                evidence = self.extractEvidence(file.iloc[idx]["evidence"][0])

                FileRow = {'id': int(file.iloc[idx]['id']), 'claim': file.iloc[idx]['claim'], 'label': int(label), 'evidence': evidence}
                MyFile.append(FileRow)
                Done += 1
            return MyFile

        
