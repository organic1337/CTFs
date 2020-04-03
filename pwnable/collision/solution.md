# Solution for collision
Well actually for this one I didn't need to write any code at all. 

The interesting part is this:
```C
unsigned long hashcode = 0x21DD09EC;
unsigned long check_password(const char* p){
        int* ip = (int*)p;
        int i;
        int res=0;
        for(i=0; i<5; i++){
                res += ip[i];
        }
        return res;
}
```
Because of how the check_password works, all I had to do was providing a pass code
that the sum of its first 5 bytes equals 0x21DD09EC. 

So all you need is a calculator and the challange is solved ;)
