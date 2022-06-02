import pandas as pd

df = pd.DataFrame({'col1': 'A', 'col2': 'C'}, {'col1': 'A', 'col2': 'D'})
print(df.loc['col1', 'col3'])