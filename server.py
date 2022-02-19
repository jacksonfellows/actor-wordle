import json
import networkx as nx

def normalize_name(name):
    if name.startswith('[[') and name.endswith(']]'):
        return name[2:-2]
    return name

import time

def make_movie_graph(path):
    start = time.time()
    G = nx.Graph()
    actor_movies = {}
    with open(path) as f:
        for line in f.readlines():
            o = json.loads(line)
            title = o['title']
            cast = [normalize_name(actor) for actor in o['cast']]
            for actor in cast:
                G.add_node(actor)
            for i,actor in enumerate(cast):
                for other_actor in cast[i+1:]:
                    if G.has_edge(actor, other_actor):
                        G.get_edge_data(actor, other_actor)['movies'].append(title)
                    else:
                        G.add_edge(actor, other_actor, movies=[title])
    print('took', time.time() - start)
    return G
        
def process_guess(G, guess, actor):
    if guess == actor:
        return {'degree': 0}
    if not G.has_node(guess):
        return {'error': 'Not a valid actor.'}
    chain = nx.shortest_path(G, guess, actor)
    degree = len(chain)-1
    movies = G.get_edge_data(chain[0], chain[1])['movies']
    return {'degree': degree, 'movies': movies}

import pickle

def save_graph(G, path):
    with open(path, 'wb') as f:
        pickle.dump(G, f)

def load_graph(path):
    print('loading graph from', path)
    with open(path, 'rb') as f:
        return pickle.load(f)

from flask import Flask, request

app = Flask(__name__)

G = load_graph('data.pickle')

@app.route('/')
def index():
    return app.send_static_file('index.html')

def get_secret_actor():
    with open('secret_actor') as f:
        actor = f.read().strip()
        assert(G.has_node(actor))
        return actor

@app.route('/guess', methods=['POST'])
def guess():
    guessed_actor = request.json['guess']
    return process_guess(G, guessed_actor, get_secret_actor())
