#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <cs50.h>
#include <ctype.h>

bool valid_key(string s);

int main(int argc, string argv[])
{
    // check if the key exists and is vaild
    if (argc != 2 || !valid_key(argv[1]))
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    int key = atoi(argv[1]);

    string plaintext = get_string("plaintext: ");
    for(int i = 0, n = strlen(plaintext); i < n; i++)
    {
        char letter = plaintext[i];
        if(isalpha(letter))
        {
            if(islower(letter))
            {
                int diff = letter - 'a';
                diff = (diff + key)%26 + 'a';
                plaintext[i] = diff;
            }
            else
            {
                int diff = letter - 'A';
                diff += (diff + key)%26 + 'A';
                plaintext[i] = diff;
            }
        }

    }

    printf("%s\n", plaintext);

    return 0;


}

// check if the key is all digits and thus valid
bool valid_key(string s)
{
    for(int i = 0, n = strlen(s); i < n; i++)
    {
        char ch = s[i];
        if(!isdigit(ch))
        {
            return false;
        }
    }
    return true;

}
