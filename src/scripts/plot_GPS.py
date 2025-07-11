import sqlite3
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import splprep, splev
import numpy as np

db_path = 'gps.db'

def remove_near_duplicates(lon, lat, alt, eps=1e-4):
    cleaned_lon = []
    cleaned_lat = []
    cleaned_alt = []
    for i in range(len(lon)):
        if i == 0 or abs(lon[i] - cleaned_lon[-1]) > eps or abs(lat[i] - cleaned_lat[-1]) > eps or abs(alt[i] - cleaned_alt[-1]) > eps:
            cleaned_lon.append(lon[i])
            cleaned_lat.append(lat[i])
            cleaned_alt.append(alt[i])
    return cleaned_lon, cleaned_lat, cleaned_alt

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM gps")
rows = cursor.fetchall()
conn.close()

latitudes = []
longitudes = []
altitudes = []

for row in rows:
    try:
        coord_str = row[1]
        lat_str, lon_str, alt_str = coord_str.split(',')
        lat = float(lat_str)
        lon = float(lon_str)
        alt = float(alt_str)

        if not any(map(np.isnan, [lat, lon, alt])):
            latitudes.append(lat)
            longitudes.append(lon)
            altitudes.append(alt)
    except Exception as e:
        print(f"Ошибка чтения строки '{row[1]}': {e}")



longitudes, latitudes, altitudes = remove_near_duplicates(longitudes, latitudes, altitudes)
print(f"Количество точек после фильтрации: {len(latitudes)}")

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot(longitudes, latitudes, altitudes, 'b', label='Raw GPS')

if len(latitudes) >= 4:
    try:
        # Вычисляем расстояния между точками
        coords_array = np.vstack([longitudes, latitudes, altitudes]).T
        distances = np.linalg.norm(np.diff(coords_array, axis=0), axis=1)
        u = np.zeros(len(coords_array))
        u[1:] = np.cumsum(distances)
        u /= u[-1]  # нормализация до [0,1]

        # Интерполяция с заданным параметром
        tck, _ = splprep(coords_array.T, u=u, s=150.0, k=3)
        u_fine = np.linspace(0, 1, 5000)
        x_spline, y_spline, z_spline = splev(u_fine, tck)

        ax.plot(x_spline, y_spline, z_spline, 'r-', label='Interpolated spline')
    except Exception as e:
        print(f"Не удалось построить сплайн: {e}")
else:
    print("Недостаточно точек для интерполяции.")

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_zlabel('Altitude')
ax.legend()

plt.title('3D GPS Trajectory with Spline')
plt.tight_layout()
plt.show()

