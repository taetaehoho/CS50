#include <cs50.h>
#include <stdio.h>
#include <math.h>

int main(void)
{
    int starting_population;
    do
    {
        starting_population = get_int("Starting Size: ");
    }
    while(starting_population < 9);

    int ending_population;
    do
    {
        ending_population = get_int("End Size: ");
    }
    while(ending_population < starting_population);

    int years = 0;

    while(ending_population > starting_population)
    {
        starting_population = starting_population + (starting_population/3) - (starting_population/4);
        years ++;
    }

    printf("Years: %i\n", years);
}