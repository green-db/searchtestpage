from core.domain import Product
import numpy as np
import datetime
import pickle
import json

index_bits = 1<<14
block_size = 32
min_ngram = 3
max_ngram = 4

def mix32(x):
	x = x + 0
	x ^= x >> 16
	x *= 0x7feb352d
	x ^= x >> 15
	x *= 0x846ca68b
	x ^= x >> 16
	return x

def roller(a, window, axis=-1):
	shape = list(a.shape)
	assert shape[axis] >= window
	shape[axis] += 1 - window
	shape.append(window)
	strides = a.strides + (a.strides[axis], )
	return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def get_text(prod):
	return [prod.name, prod.description, prod.brand]

def get_ngrams(text):
	for x in text:
		x = np.frombuffer(x.lower().encode(), dtype='uint8')
		for n in range(min_ngram, max_ngram + 1):
			if len(x) >= n:
				yield np.unique((roller(x, n) * 256**np.arange(n)).sum(-1))

def build_keys(X):
	keys = np.zeros((len(X) + (-len(X)&block_size-1), index_bits), dtype='uint8')
	for i, prod in enumerate(X):
		for x in get_ngrams(get_text(prod)):
			for h in [0, 0x16b33fb4, 0x59300865]:
				keys[i, mix32(x^h) & index_bits - 1] = 1
	return keys

class Encoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Product):
			return obj.dict()
		if isinstance(obj, (datetime.date, datetime.datetime)):
			return obj.isoformat()
		assert False, type(obj)

with open("f:/latestprods.pt", "rb") as f:
	prods = pickle.load(f)

keys = build_keys(prods)

for i in range(index_bits):
	bitmap = np.packbits(keys[:, i], bitorder='little').tobytes()
	with open(f'index/{i}', 'wb') as f:
		f.write(bitmap)

for i in range(0, len(prods), block_size):
	with open(f'blocks/{i//block_size}', 'w', encoding="utf-8") as f:
		json.dump(prods[i:i+block_size], f, cls=Encoder)
