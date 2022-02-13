import re, string, random, sys
import numpy as np

file_path = 'data/medical-corpus.txt'
_hashtag = ' <HASHTAG> '
_mention = ' <MENTION> '
_url = '<URL>'

def isURL(word):
    global _url
    # currently, the logic is based on regex
    temp = word
    word = re.sub(r"[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%.\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%\+.~#?&//=]*)", _url, word)
    if temp == word:
        return False, temp
    return True, word

def isHashtag(word):
    global _hashtag
    temp = word
    word = re.sub("#(\w+)", _hashtag, word)
    if temp == word:
        return False, temp
    return True, word

def isMention(word):
    global _mention
    temp = word
    word = re.sub("@(\w+)", _mention, word)
    if temp == word:
        return False, temp
    return True, word

def removeDupPunc(word):
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

def addSpacesForPunc(word):
    puncSet = set(string.punctuation)
    first = 0
    while first < len(word) and word[first] in puncSet:
        first += 1
    word = word[:first] + ' ' + word[first:]
    end = len(word)-1
    while first < len(word) and word[end] in puncSet:
        end -= 1
    word = word[:end] + ' ' + word[end:]
    return word

def lineTokenise(n, line):
    words = line.split(' ')
    tokens = []
    # rules for creating the tokens
    tokens = []
    for word in words:
        token = ''
        # first handle the punctuations
        ret, token = isURL(word)
        if ret == False:
            ret, token = isHashtag(token)
            ret, token = isMention(token)
            new_word = removeDupPunc(token)
            new_word = re.sub('\'', " '", new_word)
            new_words = new_word.split()
            
            for w in new_words:
                tokens.append(w)
        else:
            tokens.append(token)
    for i in range(n-1):
        tokens.insert(0, '<START>')
        tokens.insert(len(tokens), '<END>')
    return tokens

def tokenise(n, file_path):
    text_data = []
    with open(file_path) as file:
        text_data = file.readlines()
    
    tokens = []
    for line in text_data:
        tokens.append(lineTokenise(n, line))
    test_tokens = []
    return tokens, test_tokens

    # count the unigrams, bigrams, trigrams, 4-grams
def count_n_grams(n, file_path):
    counts = [dict() for i in range(n+1)]
    discounts = [dict() for i in range(n+1)]
    tokens, test_tokens = tokenise(n, file_path)
        
    for line in tokens:
        grams = [[]]
        temp = []
        for i in range(n):
            temp.append('<START>')
            grams.append(temp.copy())
        for i in range(0, len(line)):
            for num in range(1, n+1):
                grams[num].append(line[i])
                grams[num].pop(0)
                string = " ".join(grams[num])
                less_string = " ".join(grams[num-1])

                if string not in counts[num]:
                    counts[num][string] = 0
                if less_string not in discounts[num] and less_string != '':
                    discounts[num-1][less_string] = set()
                counts[num][string] += 1 
                if less_string != '':
                    discounts[num-1][less_string].add(string)
    return counts, tokens, discounts, test_tokens       

# wittenBell function for calculating the n-gram probability.
def kneyserNey(n, counts, discounts, line, index, d):
    if n == 1:
        if line[index] not in counts[1]:
            return 1e-4
        return counts[1][line[index]]/len(counts[1])

    less_gram = ''
    n_gram = ''
    for i in range(n-1, 0, -1):
        n_gram += line[index-i] + ' '
        less_gram += line[index-i] + ' '
    less_gram = less_gram[:-1]
    n_gram += line[index]
    
    if less_gram not in counts[n-1]:
        return 1e-4
    if n_gram not in counts[n]:
        return d*len(discounts[n-1][less_gram])*(kneyserNey(n-1, counts, discounts, line, index-1, d))/counts[n-1][less_gram]
    p = max(counts[n][n_gram]-d, 0) + d*len(discounts[n-1][less_gram])*(kneyserNey(n-1, counts, discounts, line, index-1, d))
    
    return p/counts[n-1][less_gram]

def wittenBell(n, counts, discounts, line, index, d):
    if n == 1:
        if line[index] not in counts[1]:
            return 1e-4
        return counts[1][line[index]]/len(counts[1])

    less_gram = ''
    n_gram = ''
    for i in range(n-1, 0, -1):
        n_gram += line[index-i] + ' '
        less_gram += line[index-i] + ' '
    less_gram = less_gram[:-1]
    n_gram += line[index]
    

    if less_gram not in counts[n-1]:
        return 1e-4
    p_ml = 0
    if n_gram in counts[n]:
        p_ml = counts[n][n_gram]/counts[n-1][less_gram]

    b = len(discounts[n-1][less_gram])
    b = b/(b + counts[n-1][less_gram])

    p = (1-b)*p_ml + b*wittenBell(n-1, counts, discounts, line, index-1, d)
    return p

counts = []
discounts = []

def findPerplexitiesForFile(n, file_path, d, type):
    global counts, discounts
    avg = 0
    probs = []
    counts, tokens, discounts, test_tokens = count_n_grams(n, file_path)

def queries(n, q):
    global counts, discounts
    n = 4
    line = lineTokenise(n, q)
    probs = 0
    d = 0.75
    for i in range(n, len(line)):
        if type == 'k':
            probs += np.log(kneyserNey(n, counts, discounts, line, i, d))
        else: 
            probs += np.log(wittenBell(n, counts, discounts, line, i, d))
    # probs *= -1/(len(line)-n+1)
    print(np.exp(probs))

if __name__ == "__main__":
    k = int(sys.argv[1])
    findPerplexitiesForFile(k, sys.argv[0], 0.75, sys.argv[2])

query = input('input sentence: ')
queries(k, query)