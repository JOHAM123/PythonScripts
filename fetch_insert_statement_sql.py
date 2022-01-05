
# Using readlines()
file1 = open('sql1.sql','r' , encoding='utf-8')
file2 = open("insert.sql","a" , encoding='utf-8')

Lines = file1.readlines()
# Strips the newline character
for line in Lines:
    if ("INSERT INTO" in line):
        file2.write(line)
file2.close()
