def main():
    """
        The solution for this challange is actually very easy. Basically
        what the executable does is writing the passwod to a temp file,
        sleep for a couple of miliseconds and then delete the file.

        What we need to do is read the temp file while the executable is
        sleeping. Therefore we could just do:
        ~/ch12 | /tmp/your_temp_dir/python3 solution.py
    """
    with open('/tmp/tmp_file.txt', 'r') as temp_file:
        print(temp_file.read())


if __name__ == '__main__':
    main()