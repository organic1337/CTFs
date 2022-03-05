# Solution

in betting function the bet amount is not checked properly, and you can bet
more money than you have:

```C
int betting() //Asks user amount to bet
{
 printf("\n\nEnter Bet: $");
 scanf("%d", &bet);
 
 if (bet > cash) //If player tries to bet more money than player has
 {
        printf("\nYou cannot bet more money than you have.");
        printf("\nEnter Bet: ");
        scanf("%d", &bet);
        return bet;
 }
 else return bet;
} // End Function
```


```
YaY_I_AM_A_MILLIONARE_LOL


Cash: $572590076
-------
|D    |
|  Q  |
|    D|
-------

Your Total is 10

The Dealer Has a Total of 10

```