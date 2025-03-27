#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 15:40:44 2021

@author: kratisaxena
"""


import wikipedia
import spacy
nlp = spacy.load('en_core_web_sm')
from allennlp.predictors.predictor import Predictor
import re, os
openie_path = "/Users/kratisaxena/Desktop/Jupyter_notebooks/Wikipedia_Knowledge_Base/openie-model.2020.03.26.tar.gz"
predictor = Predictor.from_path(openie_path)

def process_openie_arguments(sent, term):
    prediction = predictor.predict(sentence=sent)
    bracket_pattern = "\[(.*?)\]"
    list1 = prediction['verbs']
    list_of_desc = []
    for i in range(len(list1)):
        list_of_desc.append(list1[i]['description'])
    args_list = []
    for args in list_of_desc:
        args_list.append(re.findall(bracket_pattern, args))
    term_based_args_list = []
    for j in range(len(args_list)):
        count = 0
        for k in range(len(args_list[j])):
            #if "ARG0" in args_list[j][k] or "ARG1" in args_list[j][k] or "ARG2" in args_list[j][k] or "V" in args_list[j][k]:
            if term in args_list[j][k]:
                args_list[j][k] = ': '.join([args_list[j][k].split(": ")[0], term])
                count = count+1
        if count!=0:

            term_based_args_list.append(args_list[j])

    return term_based_args_list

def sentence_segmentation(text):
    text_sentences = nlp(text)
    segmented_sents = []
    for sentence in text_sentences.sents:
        segmented_sents.append(str(sentence.text))
    return segmented_sents

def lowercase_and_normalize_text_in_lists(text_list):
    for i in range(len(text_list)):
        text_list[i] = text_list[i].lower()
        text_list[i] = ' '.join(text_list[i].split())
    return text_list

def search_term_in_sent_list(term, sent_list):
    result_sents = []
    for i in range(len(sent_list)):
        if term in sent_list[i]:
            result_sents.append(sent_list[i])
    return result_sents

def create_concept_sent_dictionary(concept_list, list_of_sents):
    values = []
    for i in range(len(concept_list)):
        concept_to_search = concept_list[i]
        result_sents = search_term_in_sent_list(concept_to_search, list_of_sents)
        values.append(result_sents)
    dict_ = dict(zip(concept_list, values))
    dict_ = {k: v for k, v in dict_.items() if v!= []}
    return dict_



article = "New York City"
ny = wikipedia.page(article)
content = ny.content
link_concepts = list(ny.links)
link_concepts = lowercase_and_normalize_text_in_lists(link_concepts)
segmented_sents = sentence_segmentation(content)
segmented_sents = lowercase_and_normalize_text_in_lists(segmented_sents)

concept_occurrence_dict = create_concept_sent_dictionary(link_concepts, segmented_sents)

keys = list(concept_occurrence_dict.keys())
values =  list(concept_occurrence_dict.values())
new_values = []
for i in range(len(values)):
    print(i, " of ", len(values), " done.")
    inner = []
    for j in range(len(values[i])):
        #print(values[i][j])
        inner = process_openie_arguments(values[i][j], keys[i])
    new_values.append(inner)

query = ["CREATE (n:Article {name: \'" + article + "\'})"]
required_arg = ['ARG0', 'ARG1', 'ARG2', 'ARG-GOL', 'ARGM-LOC']
for i in range(len(new_values)):

    for j in range(len(new_values[i])):
        args_available = []

        for k in range(len(new_values[i][j])):
            if 'ARG0' in new_values[i][j][k]:
                query.append("CREATE (m:arg0 {name: \'" + new_values[i][j][k].split(": ")[1] + "\'})")
                args_available.append('ARG0')
                arg0 = new_values[i][j][k].split(": ")[1]
            if 'ARG1' in new_values[i][j][k]:
                query.append("CREATE (m:arg1 {name: \'" + new_values[i][j][k].split(": ")[1] + "\'})")
                args_available.append('ARG1')
                arg1 = new_values[i][j][k].split(": ")[1]
            if 'ARG2' in new_values[i][j][k]:
                query.append("CREATE (m:arg2 {name: \'" + new_values[i][j][k].split(": ")[1] + "\'})")
                args_available.append('ARG2')
                arg2 = new_values[i][j][k].split(": ")[1]
            if 'ARG-GOL' in new_values[i][j][k]:
                query.append("CREATE (m:arggol {name: \'" + new_values[i][j][k].split(": ")[1] + "\'})")
                args_available.append('ARG-GOL')
                arggol = new_values[i][j][k].split(": ")[1]
            if 'ARGM-LOC' in new_values[i][j][k]:
                query.append("CREATE (m:argloc {name: \'" + new_values[i][j][k].split(": ")[1] + "\'})")
                args_available.append('ARG-LOC')
                argloc = new_values[i][j][k].split(": ")[1]
            if 'V' in new_values[i][j][k]:
                rel = new_values[i][j][k].split(": ")[1]
        if 'ARG0' in args_available and 'ARG1' in args_available:
            query.append("MATCH (a:arg0),(b:arg1) WHERE a.name = \'"+arg0+"\' AND b.name = \'" + arg1 + "\' CREATE (a)-[r:"+rel+"]->(b)")
            query.append("MATCH (a:arg0),(b:Article) WHERE a.name = \'"+arg0+"\' AND b.name = \'" + article + "\' CREATE (a)-[r:HasInfoAbout]->(b)")

            if 'ARG2' in args_available:
                query.append("MATCH (a:arg1),(b:arg2) WHERE a.name = \'"+arg1+"\' AND b.name = \'" + arg2 + "\' CREATE (a)-[r:HasAdditionalInformation]->(b)")
            if 'ARG-GOL' in args_available and 'ARG2' in args_available:
                query.append("MATCH (a:arg2),(b:arggol) WHERE a.name = \'"+arg2+"\' AND b.name = \'" + arggol + "\' CREATE (a)-[r:ToOrFor]->(b)")
            if 'ARG-LOC' in args_available and 'ARG2' in args_available:
                query.append("MATCH (a:arg2),(b:argloc) WHERE a.name = \'"+arg2+"\' AND b.name = \'" + argloc + "\' CREATE (a)-[r:ToOrFor]->(b)")
            if 'ARG-GOL' in args_available and 'ARG1' in args_available and 'ARG2' not in args_available:
                query.append("MATCH (a:arg1),(b:arggol) WHERE a.name = \'"+arg1+"\' AND b.name = \'" + arggol + "\' CREATE (a)-[r:ToOrFor]->(b)")
            if 'ARG-LOC' in args_available and 'ARG1' in args_available and 'ARG2' not in args_available:
                query.append("MATCH (a:arg1),(b:argloc) WHERE a.name = \'"+arg1+"\' AND b.name = \'" + argloc + "\' CREATE (a)-[r:HasLocationInfo]->(b)")



        if 'ARG1' in args_available and 'ARG2' in args_available and 'ARG0' not in args_available:
            query.append("MATCH (a:arg1),(b:arg2) WHERE a.name = \'"+arg1+"\' AND b.name = \'" + arg2 + "\' CREATE (a)-[r:"+rel+"]->(b)")
            query.append("MATCH (a:arg1),(b:Article) WHERE a.name = \'"+arg1+"\' AND b.name = \'" + article + "\' CREATE (a)-[r:HasInfoAbout]->(b)")
            if 'ARG-GOL' in args_available:
                query.append("MATCH (a:arg2),(b:arggol) WHERE a.name = \'"+arg2+"\' AND b.name = \'" + arggol + "\' CREATE (a)-[r:ToOrFor]->(b)")
            if 'ARG-LOC' in args_available:
                query.append("MATCH (a:arg2),(b:argloc) WHERE a.name = \'"+arg2+"\' AND b.name = \'" + argloc + "\' CREATE (a)-[r:ToOrFor]->(b)")

        if 'ARG1' in args_available and 'ARG2' not in args_available and 'ARG0' not in args_available and 'ARG-LOC' in args_available:
            query.append("MATCH (a:arg1),(b:argloc) WHERE a.name = \'"+arg1+"\' AND b.name = \'" + argloc + "\' CREATE (a)-[r:HasLocationInfo]->(b)")
            query.append("MATCH (a:arg1),(b:Article) WHERE a.name = \'"+arg1+"\' AND b.name = \'" + article + "\' CREATE (a)-[r:HasInfoAbout]->(b)")
        if 'ARG1' in args_available and 'ARG2' not in args_available and 'ARG0' not in args_available and 'ARG-GOL' in args_available:
            query.append("MATCH (a:arg1),(b:arggol) WHERE a.name = \'"+arg1+"\' AND b.name = \'" + arggol + "\' CREATE (a)-[r:ToOrFor]->(b)")
            query.append("MATCH (a:arg1),(b:Article) WHERE a.name = \'"+arg1+"\' AND b.name = \'" + article + "\' CREATE (a)-[r:HasInfoAbout]->(b)")

        if 'ARG0' in args_available and 'ARG1' not in args_available and 'ARG2' not in args_available and 'ARG-LOC' in args_available:
            query.append("MATCH (a:arg0),(b:argloc) WHERE a.name = \'"+arg0+"\' AND b.name = \'" + argloc + "\' CREATE (a)-[r:HasLocationInfo]->(b)")
            query.append("MATCH (a:arg0),(b:Article) WHERE a.name = \'"+arg0+"\' AND b.name = \'" + article + "\' CREATE (a)-[r:HasInfoAbout]->(b)")
        if 'ARG0' in args_available and 'ARG2' not in args_available and 'ARG1' not in args_available and 'ARG-GOL' in args_available:
            query.append("MATCH (a:arg0),(b:arggol) WHERE a.name = \'"+arg0+"\' AND b.name = \'" + arggol + "\' CREATE (a)-[r:ToOrFor]->(b)")
            query.append("MATCH (a:arg0),(b:Article) WHERE a.name = \'"+arg0+"\' AND b.name = \'" + article + "\' CREATE (a)-[r:HasInfoAbout]->(b)")

        if 'ARG2' in args_available and 'ARG1' not in args_available and 'ARG0' not in args_available and 'ARG-LOC' in args_available:
            query.append("MATCH (a:arg2),(b:argloc) WHERE a.name = \'"+arg2+"\' AND b.name = \'" + argloc + "\' CREATE (a)-[r:HasLocationInfo]->(b)")
            query.append("MATCH (a:arg2),(b:Article) WHERE a.name = \'"+arg2+"\' AND b.name = \'" + article + "\' CREATE (a)-[r:HasInfoAbout]->(b)")
        if 'ARG2' in args_available and 'ARG1' not in args_available and 'ARG0' not in args_available and 'ARG-GOL' in args_available:
            query.append("MATCH (a:arg2),(b:arggol) WHERE a.name = \'"+arg2+"\' AND b.name = \'" + arggol + "\' CREATE (a)-[r:ToOrFor]->(b)")
            query.append("MATCH (a:arg2),(b:Article) WHERE a.name = \'"+arg2+"\' AND b.name = \'" + article + "\' CREATE (a)-[r:HasInfoAbout]->(b)")

home_path = "/Users/kratisaxena/Desktop/Jupyter_notebooks/Wikipedia_Knowledge_Base"
with open(os.path.join(home_path, "query.txt"), "w", encoding='utf-8', errors='ignore') as f:
    for q in query:
        f.write(q)
        f.write("\n")
    f.close()




with open(os.path.join(home_path, "new_values_new_york.txt"), "w", encoding='utf-8', errors='ignore') as f:
    f.write(str(new_values))

    f.close()



