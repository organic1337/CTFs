# Solution for `flag`
This challange can be solved by these steps:

- Open the elf in GDB `gdb flag`
- set breakpoint for exit_group syscall `catch exit_group`
- run the file `r`
- Export a core-dump `generate-core-file corefile`
- filter strings inside this core-dump (filter by length greater than 30 since we now pwnable's flags are long) 
 `strings -n 30 corefile`
- Find the flag from the list
  
