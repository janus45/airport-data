import json
import os
import sys
import tomllib
import requests

from views.airport import Airport, AirportData


class TomlData:
    def __init__(self, data_dir: str, output_dir: str, export: bool = True):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.data = AirportData(airports=[])

        self.checked_urls = {}
        self.errors = []

        self.load_toml_data()
        self.validate_data()

        self.check_errors()

        if export:
            self.export_data_json()

    def load_toml_data(self):
        """Loads the TOML data from the data directory."""
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(".toml"):
                    file_path = os.path.join(root, file)
                    self.process_toml(file_path)

    def process_toml(self, file_path: str):
        """Processes a single TOML file and adds its content to self.data as an Airport instance."""
        try:
            with open(file_path, "rb") as f:
                toml_content = tomllib.load(f)

            if "airport" in toml_content:
                for airport_data in toml_content["airport"]:
                    airport = Airport(**airport_data)
                    self.data.airports.append(airport)
            else:
                print(f"Warning: 'airport' key not found in {file_path}")

        except Exception as e:
            self.errors.append(f"Failed to process {file_path}: {e}")

    def validate_url(self, url: str):
        if url in self.checked_urls:
            print(
                f"URL {url} has already been checked. Valid: {self.checked_urls[url]}"
            )
            return self.checked_urls[url]

        try:
            response = requests.head(url, allow_redirects=True, timeout=2)
            print(f"Checked {url}, status code: {response.status_code}")

            is_valid = response.status_code != 404

            self.checked_urls[url] = is_valid

            return is_valid

        except requests.exceptions.RequestException as e:
            print(f"Error checking {url}: {e}")
            self.checked_urls[url] = False
            return False

    def validate_data(self):
        for element in self.data.airports:
            for link in element.links:
                url_is_valid = self.validate_url(link.url)
                if not url_is_valid:
                    self.errors.append(
                        f"Airport {element.icao} has an invalid URL, see: {link}"
                    )

    def check_errors(self):
        if len(self.errors) == 0:
            return

        for error in self.errors:
            print(error)

    def export_data_json(self):
        if len(self.errors) != 0:
            sys.exit(1)

        try:
            json_data = self.data.model_dump(mode="json")
            output_path = os.path.join(self.output_dir, "airports.json")

            with open(output_path, "w") as json_file:
                json.dump(json_data, json_file, indent=4)
            print(f"Data successfully exported to {output_path}")

        except Exception as e:
            print(f"Failed to export data to JSON: {e}")
            sys.exit(1)
