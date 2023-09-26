# pip install num2words
from num2words import num2words
# Przecinki nie działają - kropki tak
# Stringi działają

print('1 =', num2words(1, lang='pl'))
print('1 string =', num2words('1', lang='pl'))
print('1.1 =', num2words(1.1, lang='pl'))
print('1.1 string =', num2words('1.1', lang='pl'))
print('1,2 =', num2words(1,2, lang='pl')) # Pierwsz?
# print('1,2 string =', num2words('1,2', lang='pl')) # Błąd
print('1 ordinal =', num2words(1, ordinal=True, lang='pl')) # Tulko w intach
print('1 ordinal =', num2words(1, to='ordinal', lang='pl')) # Tulko w intach
print('1 ordinal =', num2words(1, to='ordinal_num', lang='pl')) # Tulko w intach
print('1 year =', num2words(1923, to='year', lang='pl')) # Tulko w intach
print('1 currency =', num2words(1923, to='currency', lang='pl')) # Tulko w intach
print(num2words(42.0, to='currency', lang='pl', currency='EUR'))
print(num2words(42, to='currency', lang='pl', currency='PLN'))
print(num2words(1925, to='year', lang='pl', currency='PLN'))

# Wyjście: "czterdzieści dwie euro"
# Outputs: "czterdzieści dwa euro"

# print(num2words(123, ordinal=True, lang='pl'))
