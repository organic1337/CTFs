def main():
    """
    Simply decode the given ascii
    """
    secret = '4C6520666C6167206465206365206368616C6C656E6765206573' \
             '743A203261633337363438316165353436636436383964356239313237356433323465'

    for i in range(0, len(secret), 2):
        print(chr(int(secret[i: i + 2], 16)), end='')


if __name__ == '__main__':
    main()
