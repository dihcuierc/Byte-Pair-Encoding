from collections import Counter
from Indexer import Indexer


class BPE():
    def __init__(self, vocab):
        self.vocab = vocab
        
    def get_pairs(self, word):
        """
        Get the character pairs in a word.
        params word: string word
        return: Returns all the possible character set of pairs in a word.
        """
        pairs = set()
        prev_char = word[0]
        for char in word[1:]:
            pairs.add((prev_char, char))
            prev_char = char
        return pairs

    def count_pairs(self, D):
        """
        Count the number of character-pairs(bigrams) in the text corpus
        params corpus: list of sentences
        Return dictionary of pairs and their counts in a corpus.
        """
        pairs = Counter()
        for word in D:
            if len(word) > 1:
                word_pairs = self.get_pairs(word)
                for pair in word_pairs:
                    pairs[pair] += 1
        return pairs

    def merge_vocab(self, pair, D, new_index):
        """
        Replace the bigram with the highest count with the new index
        params pair: bigram with highest count
        params v_in: corpus
        params new_index: new vocabulary index
        return: corpus with new index replacing bigram
        """
        v_out = []
        for word in D:
            sen = []
            i = 0
            while i < len(word):
                if word[i] == pair[0] and i < len(word)-1 and word[i+1] == pair[1]:
                    sen.append(new_index)
                    i += 2
                else:
                    sen.append(word[i])   
                    i += 1 
            v_out.append(sen)
        return v_out

    def build_vocab(self, corpus, length):
        """
        Build vocabulary of length length
        params D: list of sentences
        params vocab: Indexer
        params length: length of desired vocabulary
        return: vocab with desired length
        """
        # Build initial vocabulary
        print('Building initial vocab...')
        for sentence in corpus:
            for word in sentence:
                self.vocab.add_and_get_index(word)
                
        # build initial tokenised D
        print("Length of vocab: ", len(self.vocab))
        print('Building initial D tokens...')
        D = []
        for sentence in corpus:
            words = []
            for word in sentence:
                if word.isalpha():
                    words.append(self.vocab.index_of(word))
                else:
                    D.append(words)
                    words = []
                    words.append(self.vocab.index_of(word))
            D.append(words)
        print('Adding new vocab...')
        while len(self.vocab) < length:
            try:
                most_common_bigram = self.count_pairs(D).most_common(1)[0]
                if most_common_bigram[1] <= 2:
                    print('Not enough bigrams to add new vocab')
                    break
                most_common_pair = most_common_bigram[0]
            except IndexError:
                
                break
            pair = ''.join([self.vocab.get_object(most_common_pair[0]), self.vocab.get_object(most_common_pair[1])])
            self.vocab.add_and_get_index(pair)
            D = self.merge_vocab(most_common_pair, D, self.vocab.index_of(pair))
        print(f"Completed building vocab... Vocab length: {len(self.vocab)}")

if __name__ == '__main__':
    from datasets import load_dataset

    # Load a dataset
    dataset = load_dataset('wmt14', 'de-en')
    train_dataset = dataset['train']
    valid_dataset = dataset['validation']

    # Accessing an example
    print(train_dataset[0])
    
    #build byte-pair encoding vocabulary
    desired_vocab_size = 2000
    vocab = Indexer()
    corpus = [x['de'] for x in train_dataset[:]['translation']]

    bpe = BPE(vocab)
    bpe.build_vocab(corpus, desired_vocab_size)