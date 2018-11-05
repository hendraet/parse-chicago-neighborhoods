import argparse
import csv

import os

from gps_to_neighborhood import get_all_neighbourhoods, find_neighbourhood

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f")
    args = parser.parse_args()
    print(args.f)
    filename = args.f
    new_filename = os.path.splitext(filename)[0] + "_new" + os.path.splitext(filename)[1]

    with open(filename, "r") as csvfile_in, open(new_filename, "w+") as csvfile_out:
        reader = csv.DictReader(csvfile_in)
        reader.fieldnames = [field.lower() for field in reader.fieldnames]
        fieldnames = reader.fieldnames
        if "community area name" not in fieldnames:
            fieldnames.append("community area name")
        if "community area number" not in fieldnames:
            fieldnames.append("community area number")
        print(fieldnames)

        writer = csv.DictWriter(csvfile_out, fieldnames)
        writer.writeheader()

        neighbourhoods = get_all_neighbourhoods()
        for (i, row) in enumerate(reader):
            if i % 1000 == 0:
                print(str(i) + " done")

            if row["latitude"] and row["longitude"]:
                lat = float(row["latitude"])
                long = float(row["longitude"])

                calculated_area_id, calculated_area_name = find_neighbourhood(lat, long, neighbourhoods)
                calculated_area_name = calculated_area_name

                row["community area name"] = calculated_area_name
                row["community area number"] = calculated_area_id
            writer.writerow(row)
