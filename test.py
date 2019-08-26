import numpy as np
r = {}
for m in range(-5,6,1):
    for n in range(-5,6,1):
        r[(m,n)] = (m**2+n**2+m*n)

output = open('C:/Users/yux20/OneDrive/Desktop/results.txt',mode='w')
for row in sorted(r.items(),key=lambda x:x[1]):
    output.write(str(row[0])+'\t'+str(row[1])+'\n')
output.close()