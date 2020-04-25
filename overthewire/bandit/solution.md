# Solution for bandit CTF in overthewire
### Level 0
`cat readme`

### Level 1
`cat ./-`. Just needed to somehow escape the '-' character.

### Level 2
`cat "spaces in this filename"`.
Add quotation mark to escape the spaces.

### Level 3
Use the -a (all) flag to list hidden files as well.
```bash
cd inhere
ls -a
cat .hidden
```
### Level 4
List all the files and pass them to `file` command
to see what they contain.
```bash
ls | file
cat ./-file07
```

### Level 5
Use the find command to find a file which is:
 - Not executable
 - Readable
 - with size of 1033 bytes 

``` bash
find -not -executable -readable -size 1033c
```

Print all the human readable bytes from the file using tr with complement and delete flag.
(will delete all the characters that do not match the given pattern)

```bash
cat ./maybehere07/.file2 | tr -dc a-zA-Z0-9
```

### Level 6
password: 7jk27qwqGhBM9plV

#### Solution 1
Ok so we are told that the file is somewhere in the **system** which means
it is not neccessarily in the home dir. what we can do is as follows:

#### Solution 1
Ok so we are told that the file is somewhere in the **system** which means
it is not neccessarily in the home dir. what we can do is as follows:
- Go to homedir
- List all files (in long format)
- `grep` the result so it will include `bandit7` as owner and `bandit6` as the group.
- print the file

```bash 
cd /

# list with the following flags: 
# -r (recursive) 
# -l (long format, used for viewing the group & owner), 
# -a (show hidden files)
# Then redirect the standard error to /dev/null to remove annoying error logs. then
# Grep with -e (regular-expression) flag with a relevant regex pattern.
ls -Rla 2> /dev/null | grep -e '.*bandit7.*bandit6.*33.*'

# Find the filename that was found by the ls and cat it.
find . -name bandit7.password -exec cat {} \; 2> /dev/null1
```

#### Solution 2 (better)

```bash
# Use the find filters to find the file. 
# Look for file with bandit7 as owner
# bandit6 as group
# size of 33 bytes

# Then cat the file 
# Remove annoying errors by redirecting to /dev/null
find . -user bandit7 -group -bandit6 -size 33c -exec cat {} \; 2> /dev/null

```

### Level 7
Just look for the word `millionth` using grep
```bash 
cat data.txt | grep  millionth
```

### Level 8
password: `cvX2JJa4CFALtqS87jk27qwqGhBM9plV`

Ok so we need to find the only one unique line in `data.txt`.
We can use uniq that can delete all duplicated lines, not that uniq
only detects duplications if lines are following each other. In order
to 'group' the duplicated lines we need to use `sort` command first.

```bash
cat data.txt | sort  | uniq -u
```


### Level 9
password: `UsvVyFSfZZWbi6wgC7dAFyFuR6jQQUhR`

Data.txt is a binary file, and we now that it contains the string 
inside a line that starts with multiple '=' characters.
We can use `strings` to find all the strings in data.txt and then use `grep`

```bash
strings data.txt | grep ==
```


### Level 10
password: `truKLdjsbJ5g7yyJ2X2R0o3a5HQJFuLk`
