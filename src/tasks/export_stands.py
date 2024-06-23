import os
import csv
from statistics import mean
from views.stand import Stand


def export_hp_csv(airports: dict, output_path: str):
    """Exports the airports dict in the format as required by the homepage"""
    os.makedirs(output_path, exist_ok=True)

    for airport, stands in airports.items():
        csv_filename = os.path.join(output_path, f"{airport}.csv")

        with open(csv_filename, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["stand", "latcoord", "longcoord"])

            for stand in stands:
                lat = mean(stand.lat) if isinstance(stand.lat, list) else stand.lat
                lon = mean(stand.lon) if isinstance(stand.lon, list) else stand.lon
                writer.writerow([stand.stand, lat, lon])
