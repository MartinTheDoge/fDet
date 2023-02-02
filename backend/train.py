import torch
import transformers
import gym
from datasets.hover import HOVER
from datasets.fever import FEVER
from datasets.feverous import FEVEROUS
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler

def test():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"You are using {device}")
    
    access_token = "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"
    tokenizer = transformers.AlbertTokenizerFast.from_pretrained('Dzeniks/alberta_fact_checking', use_auth_token=access_token, longest_first=False)
    model = transformers.AlbertForSequenceClassification.from_pretrained('Dzeniks/alberta_fact_checking', use_auth_token=access_token, return_dict=True, num_labels=2)
    load = torch.load("LastBackUp.pth")
    model.load_state_dict(load)
    model.to(device)
    claim = "Albert einstein work in the field of computer science"
    evidence = "Albert Einstein (/ˈaɪnstaɪn/ EYEN-styne;[6] German: [ˈalbɛʁt ˈʔaɪnʃtaɪn] (listen); 14 March 1879 – 18 April 1955) was a German-born theoretical physicist,[7] widely acknowledged to be one of the greatest and most influential physicists of all time."

    # claim = "Miloš Zeman has been president for 10 years." 
    # evidence = "Miloš Zeman is a Czech politician serving as the third and current President of the Czech Republic since 2013."
    
    model.to(device)
    x = tokenizer.encode_plus(claim, evidence, truncation="longest_first" , max_length=512, padding="max_length", return_tensors="pt")                                     
    model.eval()
    with torch.no_grad(): 
        x = x.to(device)
        inputIDs = x["input_ids"].squeeze(1)
        attention = x["attention_mask"].squeeze(1)
        typeIds = x["token_type_ids"].squeeze(1)
        prediction = model(input_ids=inputIDs, attention_mask=attention, token_type_ids=typeIds)
    
    print(f"ArgMax: {torch.argmax(prediction.logits)}\nSoftMax: {torch.softmax(prediction.logits, dim=1)}")


def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"You are using {device}")

    access_token = "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"
    tokenizer = transformers.AlbertTokenizerFast.from_pretrained('Dzeniks/alberta_fact_checking', use_auth_token=access_token, longest_first=False)
    model = transformers.AlbertForSequenceClassification.from_pretrained('Dzeniks/alberta_fact_checking', use_auth_token=access_token, return_dict=True, num_labels=2)
    
    model.to(device)

    train_dataset = HOVER(tokenizer, "train")

    test_dataset = HOVER(tokenizer, "test")
    test_dataset0 = FEVER(tokenizer, "test")
    test_dataset1 = FEVER(tokenizer, "val")
    test_dataset2 = FEVEROUS(tokenizer, "test")

    batch_size = 8

    train_dataloader = DataLoader(
        train_dataset,
        sampler=RandomSampler(train_dataset),
        batch_size=batch_size
    )

    test_dataloader = DataLoader(
        train_dataset,
        sampler=SequentialSampler(train_dataset),
        batch_size=1
    )

    test_dataloader0 = DataLoader(
            test_dataset0,
            sampler=SequentialSampler(test_dataset0),
            batch_size=1
        )

    test_dataloader1 = DataLoader(
            test_dataset1,
            sampler=SequentialSampler(test_dataset1),
            batch_size=1
        )

    test_dataloader2 = DataLoader(
            test_dataset2,
            sampler=SequentialSampler(test_dataset2),
            batch_size=1
        )

    optimizer = torch.optim.Adam(model.parameters(), lr = 2e-6, eps = 1e-8)
    lossFn = torch.nn.CrossEntropyLoss()

    gymBase = gym.Gym("ALBERTA")

    #gymBase.trainSqce(model, 1, train_dataloader, test_dataset, lossFn, optimizer)

    gymBase.test(model, test_dataloader, lossFn)
    gymBase.test(model, test_dataloader0, lossFn)
    gymBase.test(model, test_dataloader1, lossFn)
    gymBase.test(model, test_dataloader2, lossFn)


train()