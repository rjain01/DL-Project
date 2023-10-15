import sys
sys.path.append(r'D:\DETR DL')

# from colabcode import ColabCode
# ColabCode(port=8080)

import os
from argparse import ArgumentParser
import fiftyone

import numpy as np
import torch
from torch.cuda import amp
from torch.optim import AdamW
from torch.optim.lr_scheduler import StepLR
from torch.utils.data.dataloader import DataLoader

from models import DETR, SetCriterion
from tools.dataset import collateFunction, YOLODataset
from tools.misc import baseParser, MetricsLogger, saveArguments, logMetrics, cast2Float


def main(args):
    print(args)
    saveArguments(args, args.taskName)
    torch.manual_seed(args.seed)
    device = torch.device(args.device)

    if not os.path.exists(args.outputDir):
        os.mkdir(args.outputDir)

    # load data
    dataset = YOLODataset( args.dataDir, args.targetHeight, args.targetWidth, args.numClass)
#     dataset = fiftyone.zoo.load_zoo_dataset(
#     "coco-2017",
#     split="validation",
#     label_types=["detections", "segmentations"],
#     classes=["person", "car"],
#     max_samples=50,
# )

# Visualize the dataset in the FiftyOne App
    # session = fiftyone.launch_app(dataset)
    dataLoader = DataLoader(dataset, batch_size=args.batchSize, shuffle=True, collate_fn=collateFunction,
                            pin_memory=True, num_workers=args.numWorkers)

    # load model
    model = DETR(args).to(device)
    criterion = SetCriterion(args).to(device)

    # resume training
    if args.weight and os.path.exists(args.weight):
        print(f'loading pre-trained weights from {args.weight}')
        model.load_state_dict(torch.load(args.weight, map_location=device))

    # multi-GPU training
    if args.multi:
        model = torch.nn.DataParallel(model)

    # separate learning rate
    paramDicts = [
        {"params": [p for n, p in model.named_parameters() if "backbone" not in n and p.requires_grad]},
        {
            "params": [p for n, p in model.named_parameters() if "backbone" in n and p.requires_grad],
            "lr": args.lrBackbone,
        },
    ]

    optimizer = AdamW(paramDicts, args.lr, weight_decay=args.weightDecay)
    lrScheduler = StepLR(optimizer, args.lrDrop)
    prevBestLoss = np.inf
    batches = len(dataLoader)
    logger = MetricsLogger()

    model.train()
    criterion.train()

    scaler = amp.GradScaler()

    for epoch in range(args.epochs):
        losses = []
        for batch, (x, y) in enumerate(dataLoader):
            x = x.to(device)
            y = [{k: v.to(device) for k, v in t.items()} for t in y]

            if args.amp:
                with amp.autocast():
                    out = model(x)
                # cast output to float to overcome amp training issue
                out = cast2Float(out)
            else:
                out = model(x)

            metrics = criterion(out, y)

            loss = sum(v for k, v in metrics.items() if 'loss' in k)
            losses.append(loss.cpu().item())

            # MARK: - print & save training details
            print(f'Epoch {epoch} | {batch + 1} / {batches}')
            logMetrics({k: v for k, v in metrics.items() if 'aux' not in k})
            logger.step(metrics, epoch, batch)

            # MARK: - backpropagation
            optimizer.zero_grad()
            if args.amp:
                scaler.scale(loss).backward()
                if args.clipMaxNorm > 0:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), args.clipMaxNorm)
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                if args.clipMaxNorm > 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), args.clipMaxNorm)
                optimizer.step()

        lrScheduler.step()
        logger.epochEnd(epoch)
        avgLoss = np.mean(losses)
        print(f'Epoch {epoch}, loss: {avgLoss:.8f}')

        if avgLoss < prevBestLoss:
            print('[+] Loss improved from {:.8f} to {:.8f}, saving model...'.format(prevBestLoss, avgLoss))
            if not os.path.exists(args.outputDir):
                os.mkdir(args.outputDir)

            try:
                stateDict = model.module.state_dict()
            except AttributeError:
                stateDict = model.state_dict()
            torch.save(stateDict, f'{args.outputDir}/{args.taskName}.pt')
            prevBestLoss = avgLoss
            logger.addScalar('Model', avgLoss, epoch)
        logger.flush()
    logger.close()


if __name__ == '__main__':
    
    parser = ArgumentParser('python3 train.py', parents=[baseParser()])

    # MARK: - training config
    parser.add_argument('--lr', default=1e-5, type=float)
    parser.add_argument('--lrBackbone', default=1e-5, type=float)
    parser.add_argument('--batchSize', default=8, type=int)
    parser.add_argument('--weightDecay', default=1e-4, type=float)
    parser.add_argument('--epochs', default=1500, type=int)
    parser.add_argument('--lrDrop', default=1000, type=int)
    parser.add_argument('--clipMaxNorm', default=.1, type=float)

    # MARK: - loss
    parser.add_argument('--classCost', default=1., type=float)
    parser.add_argument('--bboxCost', default=5., type=float)
    parser.add_argument('--giouCost', default=2., type=float)
    parser.add_argument('--eosCost', default=.1, type=float)

    # # MARK: - dataset
    parser.add_argument('--dataDir', default='MangoDataset/train/images', type=str)
    parser.add_argument('--annFile', default='MangoDataset/train/train.csv', type=str)

    # # MARK: - miscellaneous
    parser.add_argument('--outputDir', default='./checkpoint', type=str)
    parser.add_argument('--taskName', default='mango', type=str)
    parser.add_argument('--numWorkers', default=8, type=int)
    parser.add_argument('--multi', default=False, type=bool)
    parser.add_argument('--amp', default=False, type=bool)

    main(parser.parse_args())
    print("end")
