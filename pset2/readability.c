#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <math.h>
#include <ctype.h>

int main(void)
{
    //receive from user string of text
    string text;
    text = get_string("Text: ");

    //count the letters
    int count_letters = 0;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        if (isalpha(text[i]))
        {
            count_letters++;
        }
    }

    int count_words = 0;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        if (text[i] == ' ')
        {
            count_words++;
        }
    }
    count_words = count_words + 1;

    int count_sentences = 0;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        if (text[i] == '.' || text[i] == '!' || text[i] == '?')
        {
            count_sentences ++;
        }
    }

    //define the word ratio
    float word_ratio = 100.0/count_words;
    float coleman_liau_index = 0.0588 * count_letters * word_ratio - 0.296 * count_sentences * word_ratio - 15.8;

    if (coleman_liau_index < 1.0)
    {
        printf("Before Grade 1\n");
    }
    else if (coleman_liau_index > 16.0)
    {
        printf("Grade 16+\n");
    }
    else
    {
        coleman_liau_index = round(coleman_liau_index);
        printf("Grade %i\n", (int) coleman_liau_index);
    }

}