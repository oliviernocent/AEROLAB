import pandas as pd
import matplotlib.pyplot as plt

tcx = pd.read_csv('reports/2022-03-21/merge_tcx_hexoskin.csv')
gpx = pd.read_csv('reports/2022-03-21/merge_gpx_hexoskin.csv')

plt.plot(tcx['Timestamp'], tcx['Speed'], label='TCX')
plt.plot(gpx['Timestamp'], gpx['Speed'], alpha=0.3, label='GPX')
plt.legend()
plt.show()