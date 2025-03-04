#!/usr/bin/env python

import sys
import os.path as osp
from vqaIngestion import VQA, VQAEval
import matplotlib.pyplot as plt
import skimage.io as io
import json
import random
import os
import argparse
import pprint

#TODO: turn into class

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results")
    parser.add_argument("--annotations")
    parser.add_argument("--questions")
    parser.add_argument("--image_dir")
    parser.add_argument("--data_dir", default=".")
    parser.add_argument("--version", default="v2")
    parser.add_argument("--task", default="OpenEnded")
    parser.add_argument("--data", default="mscoco")
    parser.add_argument("--data_subtype", default="val2014")

    return parser.parse_args()


args = parse_args()

pprint.pprint(vars(args))

# set up file names and paths
data_dir = args.data_dir
version = args.version  # this should be 'v2' when using VQA v2.0 dataset
# 'OpenEnded' only for v2.0. 'OpenEnded' or 'MultipleChoice' for v1.0
task = args.task
# 'mscoco' only for v1.0. 'mscoco' for real and 'abstract_v002' for abstract for v1.0.
data = args.data
data_subtype = args.data_subtype

ann_file = args.annotations or '{args.data_dir}/Annotations/{args.version}_{args.data}_{args.data_subtype}_annotations.json'.format(
    args=args)
ques_file = args.questions or '{args.data_dir}/Questions/{args.version}_{args.task}_{args.data}_{args.data_subtype}_questions.json'.format(
    args=args)

img_dir = args.image_dir or '{args.data_dir}/Images/{args.data}/{args.data_subtype}/'.format(
    args=args)
file_types = ['results', 'accuracy', 'evalQA', 'evalQuesType', 'evalAnsType']

# An example result json file has been provided in './Results' folder.

file_template = "{data_dir}/Results/{version}_{task}_{data}_{data_subtype}_{file_type}.json"
[res_file, accuracyFile, evalQAFile, evalQuesTypeFile, evalAnsTypeFile] = [file_template.format(
    data_dir=data_dir, version=version, task=task, data=data, data_subtype=data_subtype, file_type=file_type) for file_type in file_types]

res_file = args.results or res_file

# create vqaHelpers object and vqaRes object
vqa = VQA(ann_file, ques_file)
vqaRes = vqa.loadRes(res_file, ques_file)

# create vqaEval object by taking vqaHelpers and vqaRes
# n is precision of accuracy (number of places after decimal), default is 2
vqaEval = VQAEval(vqa, vqaRes, n=3)

# evaluate results
"""
If you have a list of question ids on which you would like to evaluate your results, pass it as a list to below function
By default it uses all the question ids in annotation file
"""
vqaEval.evaluate()

# print accuracies
print("\n")
print("Overall Accuracy is: %.02f\n" % (vqaEval.accuracy['overall']))
print("Per Question Type Accuracy is the following:")
for quesType in vqaEval.accuracy['perQuestionType']:
    print("%s : %.02f" %
          (quesType, vqaEval.accuracy['perQuestionType'][quesType]))
print("\n")
print("Per Answer Type Accuracy is the following:")
for ansType in vqaEval.accuracy['perAnswerType']:
    print("%s : %.02f" % (ansType, vqaEval.accuracy['perAnswerType'][ansType]))
print("\n")
# demo how to use evalQA to retrieve low score result
# 35 is per question percentage accuracy
evals = [quesId for quesId in vqaEval.evalQA if vqaEval.evalQA[quesId] < 35]
if len(evals) > 0:
    print('ground truth answers')
    randomEval = random.choice(evals)
    randomAnn = vqa.loadQA(randomEval)
    vqa.showQA(randomAnn)

    print('\n')
    print('generated answer (accuracy %.02f)' % (vqaEval.evalQA[randomEval]))
    ann = vqaRes.loadQA(randomEval)[0]
    print("Answer:   %s\n" % (ann['answer']))

    imgId = randomAnn[0]['image_id']
    imgFilename = 'COCO_' + data_subtype + '_' + str(imgId).zfill(12) + '.jpg'
    if os.path.isfile(img_dir + imgFilename):
        I = io.imread(img_dir + imgFilename)
        plt.imshow(I)
        plt.axis('off')
        plt.show()

# plot accuracy for various question types
plt.bar(range(len(vqaEval.accuracy['perQuestionType'])),
        vqaEval.accuracy['perQuestionType'].values(), align='center')
plt.xticks(range(len(vqaEval.accuracy['perQuestionType'])),
           vqaEval.accuracy['perQuestionType'].keys(), rotation='0', fontsize=10)
plt.title('Per Question Type Accuracy', fontsize=10)
plt.xlabel('Question Types', fontsize=10)
plt.ylabel('Accuracy', fontsize=10)
plt.show()

# save evaluation results to ./Results folder
json.dump(vqaEval.accuracy,     open(accuracyFile,     'w'))
json.dump(vqaEval.evalQA,       open(evalQAFile,       'w'))
json.dump(vqaEval.evalQuesType, open(evalQuesTypeFile, 'w'))
json.dump(vqaEval.evalAnsType,  open(evalAnsTypeFile,  'w'))
