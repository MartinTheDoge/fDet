import time
from time import strftime
import torch

class Gym():
    def __init__(self, name="Model") -> None:
        self.name = name
        self.modelPath = f"{name}.pth"
        self.loss = None
        self.acc = None

    def train(self, model, dataLoader, lossFn, optimizer) -> None:
        dataSize = len(dataLoader.dataset)
        model.train()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        for batch, (x,y) in enumerate(dataLoader):

            x = x.to(device)
            y = y.to(device)

            inputIDs = x["input_ids"].squeeze(1)
            attention = x["attention_mask"].squeeze(1)
            typeIds = x["token_type_ids"].squeeze(1)

            prediction = model(input_ids=inputIDs, attention_mask=attention, token_type_ids=typeIds)
            loss = lossFn(prediction.logits, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if batch % 100 == 0:
                loss, progress = loss.item(), batch * len(y)
                log = f"loss: {loss:>8f}, [{progress:>5f}/{dataSize:>5f}]\n"
                print(log)
    
    def calculateAccLoss(self, corrects, loss, batch_num, lossFn, prediction, label):
        loss += lossFn(prediction.logits, label)
        corrects += ((1 / (batch_num + 1)) * (loss.item() - corrects))
        return corrects, loss 

    def calculateAccLossPress(self, corrects, loss, lossFn, prediction, label, id):
        if torch.argmax(prediction.logits) == label:
            corrects += 1
        else:
            with open("testError.txt", "a") as f:
                f.write(f"{id}\n")
        loss += lossFn(prediction.logits, label)
        return corrects, loss

    def test(self, model, dataLoader, lossFn) -> None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        dataSize = len(dataLoader.dataset)
        numBatches = len(dataLoader)
        model.eval()
        loss, correct, correct2, loss2 = 0, 0, 0, 0
        with torch.no_grad():
            for batch, (x,y) in enumerate(dataLoader):        
                x = x.to(device)
                y = y.to(device)

                inputIDs = x["input_ids"].squeeze(1)
                attention = x["attention_mask"].squeeze(1)
                typeIds = x["token_type_ids"].squeeze(1)

                prediction = model(input_ids=inputIDs, attention_mask=attention, token_type_ids=typeIds)
                correct, loss = self.calculateAccLoss(correct, loss, batch, lossFn, prediction, y)
                correct2, loss2 = self.calculateAccLossPress(correct2, loss2, lossFn, prediction, y, batch)
        
        loss /= numBatches
        loss2 /= numBatches
        correct /= dataSize
        correct2 /= dataSize
        self.loss = loss
        self.acc = correct
        log = f"Results: \n Test Error: {(100*correct):>0.1f}%, Avg loss: {loss:>8f} \n My Accuracy: {(100*correct2):>0.1f}%, Avg loss: {loss2:>8f}\n"
        print(log)


    def trainSqce(self, model, Epochs, TrainDataLoader, TestdataLoader, lossFn, optimizer) -> None:
        start_time = time.perf_counter()
        for i in range(Epochs):
            EpochLog = f"\nEpoch {i + 1} \n---------------------------------\n"
            print(EpochLog)
            self.train(model, TrainDataLoader, lossFn, optimizer)
            epochTime = f"--- {(time.perf_counter() - start_time)} seconds ---\n" 
            print(epochTime)
            torch.save(model.state_dict(), "LastBackUp.pth") 
            end = strftime(f"LastBackUp{i} saved!!! %H%M-%d-%m")
            print(end)
        self.test(model, TestdataLoader, lossFn)
        self.saveModel(model=model, Epochs=Epochs, optimizer=optimizer)

    def saveModel(self, model, Epochs, optimizer, loss = None, acc = None) -> None:
        torch.save(model.state_dict(), "LastBackUp.pth")
        if loss == None:
            try: loss = self.loss
            except: pass
        if acc == None:
            try: acc = self.acc
            except: pass
        torch.save(
            {
            'epoch': Epochs,
            'model_state_dict': model.state_dict(),
            'loss' : loss,
            'accuracy' : acc
            }, self.modelPath)
        log = strftime(f"{self.name} saved!!! %H%M-%d-%m")
        print(log)

