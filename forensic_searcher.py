#! C:\Users\Khab\Desktop\SandboxPython python3
#coding:utf8
import PyPDF2
import argparse
import re
import exifread
import sqlite3

class Forensic_tool:

    @staticmethod
    def get_pdf_metadata(file_name):
        pdf_file = PyPDF2.PdfFileReader(open(file_name, "rb"))
        doc_info = pdf_file.getDocumentInfo()
        for info in doc_info:
            print("[+]",info,"+", doc_info[info])

    @staticmethod
    def get_strings(file_name):
        with open(file_name, "rb") as file:
            content = file.read()
        _re = re.compile("[\S\s]{4,}]")
        for match in _re.findall(content.decode("utf8", "backslashreplace")):
            print(match)

    @staticmethod
    def get_gps_from_exif(file_name):
        with open(file_name, "rb") as file:
            exif = exifread.process_file(file)
            if not exif:
                print("No Exif Metadata here!")
            else:
                latitude = exif.get("GPS GPSLatitude")
                latitude_ref = exif.get("GPS GPSLatitudeRef")
                longitude = exif.get("GPS GPSLongitude")
                longitude_ref = exif.get("GPS GPSLongitudeRef")
                if latitude and longitude and longitude_ref and latitude_ref:
                    lat = _convert_to_degress((latitude))
                    lon = _convert_to_degress((longitude))
                    if str(latitude_ref) != "N":
                        lat = 0 - lat
                    if str(longitude_ref) != "E":
                        lon = 0 - lon
                    print("Latitude:", lat, "\tLongitude:", lon)
                    print(f"Localisation sur Maps: http://maps.google.com/maps?q=loc:{str(lat)},{str(lon)}")

    @staticmethod
    def get_exif(file_name):
        with open(file_name, "rb") as file:
            exif = exifread.process_file(file)
            if not exif:
                print("No Exif Metadata here!")
            for tag in exif.keys():
                print(tag + " " + str(exif[tag]))

    @staticmethod
    def get_firefox(db_name):
        try:
            connection = sqlite3.connect(db_name)
            cursor = connection.cursor()
            cursor.execute("SELECT url,datetime(last_visit_date/1000000, \"unixepoch\") "
                           "FROM moz_places, moz_historyvisits WHERE visit_count > 0 AND"
                           " moz_places.id == moz_historyvisits.place_id")
            header = "<!DOCTYPE html><head><style>table,th,tr{border: 1px solid blue;}</style>" \
                     "</head><body><table><tr><th>URL</th><th>DATE</th></tr>"
            with open ("log_firefox.html", "w") as file:
                file.write(header)
                for row in cursor:
                    url = str(row[0])
                    date = str(row[1])
                    file.write("<tr><td><a href='"+url+"'>"+ url+ "</a></td><td>"+ date+ "</td></tr>")
                footer = "</table></body></html>"
                file.write(footer)
        except Exception as e:
            print("[-] Erreur", str(e))

    @staticmethod
    def get_cookies(cookies_sqlite):
        try:
            connection = sqlite3.connect(cookies_sqlite)
            cursor = connection.cursor()
            cursor.execute("SELECT name,value,host FROM moz_cookies")
            with open ("log_cookie.html", "w") as file:
                header = "<!DOCTYPE html><head><style>table,th,tr{border: 1px solid blue;}</style>" \
                         "</head><body><table><tr><th>HOST</th><th>NAME</th><th>VALUE</th></tr>"
                file.write(header)
                for row in cursor:
                    name = str(row[0])
                    value = str(row[1])
                    host = str(row[2])
                    file.write("<tr><td><a href='"+host+"'>"+ host+ "</a></td><td>"+ name+ "</td>"
                               + "<td>"+ value+ "</td></tr>")
                footer = "</table></body></html>"
                file.write(footer)
        except Exception as e:
            print("[-] Erreur", str(e))


def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)

tool = Forensic_tool()
parser = argparse.ArgumentParser(description="Forensics Tool")
parser.add_argument("-pdf", dest="pdf", help="Path to pdf file", required=False)
parser.add_argument("-str", dest="str", help="Path to file to search for Regex", required=False)
parser.add_argument("-exif", dest="exif", help="Path to file to search for exif data", required=False)
parser.add_argument("-gps", dest="gps", help="Get GPS coordinates with exif metadata", required=False)
parser.add_argument("-sql", dest="sql", help="Get Firefox history", required=False)
parser.add_argument("-coo", dest="cookie", help="Get Firefox cookies", required=False)
args = parser.parse_args()

if args.pdf:
    tool.get_pdf_metadata(args.pdf)

if args.str:
    tool.get_strings(args.str)

if args.exif:
    tool.get_exif(args.exif)

if args.gps:
    tool.get_gps_from_exif(args.gps)

if args.sql:
    tool.get_firefox(args.sql)

if args.cookie:
    tool.get_cookies(args.cookie)

