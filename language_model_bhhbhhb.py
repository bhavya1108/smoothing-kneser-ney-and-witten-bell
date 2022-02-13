import numpy
import re
import random
import sys
from collections import Counter
import string

def mention_(word):
    temp = word
    word = re.sub("@(\w+)", " <MENTION>" , word)
    if temp == word:
        return False, temp
    return True, word

def dupl_punc_(word):
    punc_set = set(string.punctuation)
    new_word = ''
    last = '4'
    for letter in word:
        if letter in punc_set:
            if last != letter:
                new_word += letter
                last = letter
        else:
            last = letter

            new_word += letter
    return new_word

def url_(word):
    var = word
    word = re.sub(r"[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)", " <URL>", word)
    if var == word:
        return False, var 
    return True , word

def hashtag_(word):
    temp = word
    word = re.sub("#(\w+)", " <HASHTAG>", word)
    if temp == word:
        return False, temp
    return True, word


def split_lines(line,n):
    words = line.split(" ")
    tokens = []
    for word in words:
        tok =''
        ret, tok = url_(word)
        if ret == False:
            ret,tok = hashtag_(tok)
            ret,tok = mention_(tok)
            new_word = dupl_punc_(tok)
            new_word = re.sub('\'', " '", new_word)
            new_word = new_word.split()

            for w in new_word:
                tokens.append(w)
        else:
            tokens.append(tok)
    token = ' '.join(tokens)
    for i in range(n-1):
        tokens.insert(0, '<START>')
        tokens.insert(len(tokens), '<END>')
    return tokens
        

def tokenize(file_p,n):
    # lines.append("#ieroween THE STORY OF IEROWEEN! THE VIDEO -»»»»»»»»»»» http://bit.ly/2VFPAV «« JUST FOR FRANK !!! ÃƒÂ§")
    lines = []
    
    with open(file_p) as f:
        lines = f.readlines()
    tokens = ""
    for line in lines:
        tokens += split_lines(line[:-1],n) + "\n"
    # print(tokens)
    return tokens

# tok = tokenize("./data/general-tweets.txt",4)
# with open("2019101095_tokenize.txt","w") as file:
#     file.write(tok)
# print(tok)


ngrams_c = {}
ngram = []
unigram = []
bigram = []
trigram = []

def find_val(gram):
    if len(gram) == 0:
        return sum(ngrams_c[1].values())
    if gram in ngrams_c[len(gram)].keys():
        return ngrams_c[len(gram)][gram] 
    else:
        return 0

def witten2(gram):
    unique = 0
    for c in ngrams_c[len(gram)+1].keys():
        if(c[:-1] == gram):
            
            unique += 1
    k = float(unique + int(find_val(gram)))
    if(k != 0):
        return (unique / k)
    else:
        return random.uniform(0.00001,0.0001)

def witten(gram):
    x = len(gram)
    if x == 1:
        return find_val(gram) / sum(ngrams_c[1].values())
    if(find_val(gram[:-1]) != 0):
        return ((1 - witten2(gram[:-1])) * (find_val(gram) / find_val(gram[:-1]))) + (witten2(gram[:-1]) * witten(gram[:-1]))
    else:
        return random.uniform(0.00001, 0.0001) +  (witten2(gram[:-1]) * witten(gram[:-1]))
    
def kneser(gram, maxi):
    x = len(gram)
    d = 0.75
    if find_val(gram[:-1]) == 0:
        lamda = random.uniform(0,1)
        term = random.uniform(0.00001,0.0001)
    else:
        if x == maxi:
            term = max(0,find_val(gram)-d)/find_val(gram[:-1])
        else:
            term = max(0,(sum(token[1:] == gram for token in ngrams_c[len(gram) + 1].keys()) - d)) / find_val(gram[:-1])
        lamda = d * sum(token[:-1] == gram[:-1] for token in ngrams_c[len(gram)].keys()) / find_val(gram[:-1])
    if x == 1:
       return term
    else:
        return term + lamda * kneser(gram[:-1], maxi)

if __name__ == '__main__':
    n = int(sys.argv[1])
    t = sys.argv[2]
    f=open(sys.argv[3], "r")
    # lines2 = []
    
    # with open("fi") as f:
    lines2 = f.readlines()
    tokens = []
    for line in lines2:
        tokens = (split_lines(line,n))
        for w in range(0,len(tokens)):
            unigram.append(tuple(tokens[w]))
    
    ngrams_c[1] = Counter(unigram)  

    for line in lines2:
        tokens = (split_lines(line,n))
        for w in range(0,len(tokens)-1):
            bigram.append(tuple(tokens[w:w+2]))

    ngrams_c[2] = Counter(bigram)
    
    for line in lines2:
        tokens = (split_lines(line,n))
        for w in range(0,len(tokens)-2):
            trigram.append(tuple(tokens[w:w+3]))

  

    ngrams_c[3] = Counter(trigram) 

    for line in lines2:
        tokens = (split_lines(line,n))
        for w in range(0,(len(tokens)-n+1)):
            ngram.append(tuple(tokens[w:w+n]))
 
    ngrams_c[4] = Counter(ngram)   
    inp = input("Input sentence: ")


    words = split_lines(inp,n)
    tex = []
    ngram_inp = []

    for x in range(0,len(words)-n+1):
        tex.append(tuple(words[x:x+n]))

    ngram_inp = Counter(tex)
    
    p = 1
    if t == 'k':
        for gram in ngram_inp:
            pp = ( 1.0 / kneser(gram,len(gram)))**(1.0/N)
            p = p*pp    
    elif t == 'w':
        for gram in ngram_inp:
            pp = ( 1.0 / witten(gram))**(1.0/N)
            p = p*pp   
        
    print(p)