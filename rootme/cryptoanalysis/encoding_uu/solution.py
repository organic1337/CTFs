from encodings.uu_codec import uu_encode, uu_decode


def main():
    """
    UU Encoding stands for - Unix to Unix encoding. This encoding is a binary to text encoding
    that was originally made for transferring files from one unix machine to another, without
    the data being corrupted.

    Good explanation about the algorithm can be found here:
    https://en.wikipedia.org/wiki/Uuencoding
    """
    encoded_text = b'''    
_=_ 
_=_ Part 001 of 001 of file root-me_challenge_uudeview
_=_ 

begin 644 root-me_challenge_uudeview
B5F5R>2!S:6UP;&4@.RD*4$%34R`](%5,5%)!4TE-4$Q%"@``
`
end
    '''

    print(uu_decode(encoded_text))


if __name__ == '__main__':
    main()
