// Implements a dictionary's functionality
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include <strings.h>
#include <ctype.h>

#include "dictionary.h"



// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Number of buckets in hash table
const unsigned int N = 100000;

// Hash table
node *table[N];

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    int index = hash(word);

    for (node *n = table[index]; n != NULL; n = n -> next)
    {
        if (strcasecmp(word, n -> word) == 0)
        {
            return true;
        }
    }
    return false;
}

// Hashes word to a number from https://stackoverflow.com/questions/7666509/hash-function-for-string
unsigned int hash(const char *word)
{
    unsigned long hash = 5381;
    int c;
    while ((c = tolower(*word++)))
    {
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
    }
    return hash % N;
}

int word_count = 0;

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    FILE *dict_ptr = fopen(dictionary, "r");
    if (dict_ptr == NULL)
    {
        printf("Unable to open dictionary\n");
        return false;
    }
    char phrase[LENGTH + 1];

    while(fscanf(dict_ptr, "%s", phrase) != EOF)
    {
        node *n = malloc(sizeof(node));
        if (n == NULL)
        {
            return false;
        }
        strcpy(n -> word, phrase);

        int index = hash(phrase);

        if (table[index] == NULL)
        {
            table[index] = n;
            table[index] -> next = NULL;
            word_count++;
        }
        else
        {
            n -> next = table[index];
            table[index] = n;
            word_count++;
        }
    }
    fclose(dict_ptr);

return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    return word_count;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
   for (int i = 0; i < N; i++)
   {
        node *n = table[i];
        while (n != NULL)
        {
            node *tmp = n;
            n = n -> next;
            free(tmp);
        }
        if (n == NULL && i == N - 1)
        {
            return true;
        }
   }
   return false;
}
