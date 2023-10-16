# DETR: End-to-End Object Detection Using Transformers


DETR addresses object detection as a direct set prediction problem, in contrast to conventional computer vision techniques. It is composed of a Transformer encoder-decoder architecture and a set-based global loss that uses bipartite matching to enforce unique predictions. DETR generates the final set of predictions in parallel by reasoning about the relationships between the objects and the global visual context, given a fixed small set of learned object queries. DETR is incredibly quick and effective because of its parallel nature.

![image](https://github.com/rjain01/DL-Project/assets/84587662/71d2cf9d-fc8f-421c-8ddf-4d3b373c8bbd)


In this project, we've have tried to implement the original paper of [DETR: End-to-End Object Detection Using Transformers](https://arxiv.org/abs/2005.12872). We've executed and compared implementations using two different backbones i.e ResNet-50 and DenseNet. We've used particular number of classes and also added support for negative samples (no object) training.

![image](https://github.com/rjain01/DL-Project/assets/84587662/8d8afbfa-31fe-480a-906e-f42c4e1b19cb)


### Contributors:
1. Archish More
2. Sanjana Gattraddy
3. Vartika Vaish
4. Riya Jain
5. Gaurang Kachhia


### Data Preparation
The directory structure of the dataset is as follows:
```
path/to/data/
	abc.jpg
	abc.txt
```
Each `.jpg` has its corresponding annotation file `.txt`. Each line in `.txt` file contains `classIndex CenterX CenterY Width Height`.


The path to the dataset directory is `MangoDataset/train/new`. We've also created `.csv` file of annotations whose path is `MangoDataset/train/train.csv`. The dataset can be downloaded from [Mango Image Dataset](https://universe.roboflow.com/fruit-dataset-1/mango-image). The dataset was used in YOLO format as per the requirements.


### Usage
After cloning the project repository, install the required libraries using:
```
pip install -r requirements.txt
```

For execution, run the main `train.py` file :
```
python3 train.py --dataDir "path_to_your_training_data" --numClass "number_of_classes" --numQuery "number_of_queries"
```


