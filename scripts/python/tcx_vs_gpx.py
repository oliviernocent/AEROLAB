import pandas as pd
import matplotlib.pyplot as plt

tcx = pd.read_csv('data/2022-03-22/merged_gpx_hexoskin_data.csv')
gpx = pd.read_csv('data/2022-03-22/merged_tcx_hexoskin_data.csv')

plt.plot(tcx['Timestamp'], tcx['Distance'], label='TCX')
plt.plot(gpx['Timestamp'], gpx['Distance'], alpha=0.3, label='GPX')
plt.legend()
plt.show()