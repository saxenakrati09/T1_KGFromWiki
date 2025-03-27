#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 17:48:40 2021

@author: kratisaxena
"""

import wikipediaapi
import pywikibot as pw
import networkx as nx
import matplotlib.pyplot as plt


site = pw.Site('en', 'wikipedia')
wiki_wiki = wikipediaapi.Wikipedia('en')

def create_class_heirarchy(article):
    category = []
    for cat in pw.Page(site, article).categories():
        if 'hidden' not in cat.categoryinfo:
            category.append(cat.title())
    # print(category)
    category_cleaned = []
    for cat in category:
        x = cat.replace("Category:", "")
        category_cleaned.append(x)
    return category_cleaned

def create_category_graph(article, iterations):
    #nodes = []
    edges = []
    nodes = [[article]]
    for i in range(0, iterations):
        if i==0:
            print(article)
            category = create_class_heirarchy(article)
            nodes.append(category)
            print(i, category)
            for cat in category:
                edges.append((article, cat))

        else:
            print(i, category)
            new_category = []
            for cat in category:
                article = "Category:"+cat
                print(article)
                category2 = create_class_heirarchy(article)
                new_category.append(category2)
                nodes.append(category2)
                for nod in category2:
                    edges.append((cat, nod))

            category = [item for sublist in new_category for item in sublist]
    nodes = [item for sublist in nodes for item in sublist]
    return nodes, edges

if __name__=="__main__":
    article = 'Coating'
    nodes, edges = create_category_graph(article, 3)
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    print(nx.info(G))
    print("\n")
    print("nodes", nodes)

    print("\n")
    print("edges", edges)
    fig = plt.Figure(figsize=(50,50))
    nx.draw_planar(G, with_labels=True)

    plt.show()
