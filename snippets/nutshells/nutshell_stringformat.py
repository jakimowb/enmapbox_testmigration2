
#rtfm https://pyformat.info/#string_truncating

#integers
value = 1233 #integer
print(value)
print('{}'.format(value)) #this is the same
print('{:+}'.format(value)) #show with - or +
print('{:10}'.format(value)) #occupy a minimum space of at least 10 characters, right aligned
print('{:>10}'.format(value)) #same as before
print('{:<10}'.format(value)) #same as before, but left aligned

#floats
import math
value = math.pi
print(value)
print('{:0.2f}'.format(value)) #print round to 2 places behind comma
print('{:+0.2f}'.format(value))
print('{:+0.2e}'.format(value)) #scientific notation (for very large / low numbers)
print('{:+0.2f}'.format(42)) #converts int to float


#strings
print('{:>10s}|next text'.format('hello')) #right aligned
print('{:<10s}|next text'.format('hello')) #left aligned

print('{:.10}'.format('this is a very long string we truncate to a length of 10 characters'))

