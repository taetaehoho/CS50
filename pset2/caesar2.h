#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <cs50.h>
#include <ctype.h>

int main(int argc, string argv[])
{
    // check if the key exists and is vaild
    if (argc != 2 || !valid_key(argv[1]))
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    int key = atoi(argv[1])

    string plaintext = get_string("plaintext: \n");
    for(int i = 0, n = strlen(plaintext); i < n; i++)
    {
        if(isalpha(plaintext[i]))
        {
            plaintext[i] += 1;

        }
    }

    return 0;


}

// check if the key is all digits and thus valid
bool valid_key(string s)
{
    for(int i = 0, n = strlen(s); i < n; i++)
    {
        if(!isdigit[i])
        {
            return false;
        }
        else
        {
            return true;
        }
    }
}