# project.py


import pandas as pd
import numpy as np
np.set_printoptions(legacy='1.21')
from pathlib import Path
import re
import requests
import time


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------

last_request_time = None
def get_book(url):
    global last_request_time
    
    robots = requests.get("https://gutenberg.org/robots.txt").text
    
    delay = 0.5
    for line in robots.split('\n'):
        if line.lower().startswith("crawl-delay"):
            try:
                delay = float(line.split(":")[1].strip())
            except:
                pass
    
    if last_request_time is not None:
        elapsed = time.time() - last_request_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
    
    response = requests.get(url)
    text = response.text
    last_request_time = time.time()
    
    text = text.replace('\r\n', '\n')
    
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
    
    start_index = text.index(start_marker)
    start_index = text.index('\n', start_index)
    
    end_index = text.index(end_marker)
    
    return text[start_index:end_index]


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def tokenize(book_string):
    text = book_string.replace('\r\n', '\n')
    paragraphs = re.split(r'\n{2,}', text)
    tokens = []
    
    for p in paragraphs:
        words = re.findall(r"[A-Za-z0-9_]+|[^\w\s]", p)
        if words:
            tokens.append('\x02')
            tokens.extend(words)
            tokens.append('\x03')
    
    if not tokens:
        return ['\x02', '\x03']
    
    return tokens


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


class UniformLM(object):


    def __init__(self, tokens):

        self.mdl = self.train(tokens)
        
    def train(self, tokens):
        unique = pd.Index(tokens).unique()
        prob = 1 / len(unique)
        return pd.Series(prob, index=unique)
    
    def probability(self, words):
        probs = self.mdl.reindex(words)
        if probs.isna().any():
            return 0
        return probs.prod()
        
    def sample(self, M):
        sampled = np.random.choice(self.mdl.index, size=M, replace=True)
        return " ".join(sampled)


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


class UnigramLM(object):
    
    def __init__(self, tokens):
        self.mdl = self.train(tokens)
    
    def train(self, tokens):
        counts = pd.Series(tokens).value_counts()
        probs = counts / counts.sum()
        return probs
    
    def probability(self, words):
        probs = self.mdl.reindex(words)
        if probs.isna().any():
            return 0
        return probs.prod()
        
    def sample(self, M):
        sampled = np.random.choice(
            self.mdl.index,
            size=M,
            replace=True,
            p=self.mdl.values
        )
        return " ".join(sampled)


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


class NGramLM(object):
    
    def __init__(self, N, tokens):
        # You don't need to edit the constructor,
        # but you should understand how it works!
        
        self.N = N

        ngrams = self.create_ngrams(tokens)

        self.ngrams = ngrams
        self.mdl = self.train(ngrams)

        if N < 2:
            raise Exception('N must be greater than 1')
        elif N == 2:
            self.prev_mdl = UnigramLM(tokens)
        else:
            self.prev_mdl = NGramLM(N-1, tokens)

    def create_ngrams(self, tokens):
        return [tuple(tokens[i:i+self.N]) 
                for i in range(len(tokens) - self.N + 1)]
        
    def train(self, ngrams):
        df = pd.DataFrame({'ngram': ngrams})
        df['n1gram'] = df['ngram'].apply(lambda x: x[:-1])
        
        ngram_counts = df['ngram'].value_counts()
        n1gram_counts = df['n1gram'].value_counts()
        
        df = df.drop_duplicates()
        df['prob'] = df['ngram'].map(ngram_counts) / df['n1gram'].map(n1gram_counts)
        
        return df[['ngram', 'n1gram', 'prob']].reset_index(drop=True)
    
    
    def probability(self, words):
        words = tuple(words)
        
        if len(words) < self.N:
            return self.prev_mdl.probability(words)
        
        prob = 1
        
        prefix = words[:self.N-1]
        prob *= self.prev_mdl.probability(prefix)
        
        for i in range(self.N-1, len(words)):
            ngram = words[i-self.N+1:i+1]
            row = self.mdl[self.mdl['ngram'] == ngram]
            if row.empty:
                return 0
            prob *= row['prob'].iloc[0]
        
        return prob
    

    def sample(self, M):
        result = ['\x02']
        
        while len(result) - 1 < M:
            
            if len(result) < self.N:
                next_token = self.prev_mdl.sample(1)
                result.append(next_token)
                continue
            
            prefix = tuple(result[-(self.N - 1):])
            subset = self.mdl[self.mdl['n1gram'] == prefix]
            
            if subset.empty:
                result.append('\x03')
                continue
            
            tokens = subset['ngram'].apply(lambda x: x[-1]).values
            probs = subset['prob'].values
            
            next_token = np.random.choice(tokens, p=probs)
            result.append(next_token)
        
        result[-1] = '\x03'
        return " ".join(result)