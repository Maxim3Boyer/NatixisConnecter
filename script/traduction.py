import os
import csv

INPUT_DIR = "output"
OUTPUT_DIR = "output_html"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def convert_csv_to_html(file_path):
    name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = os.path.join(OUTPUT_DIR, name + ".html")

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    html = []
    html.append("<html><body>")
    html.append("<table>")

    for i, row in enumerate(rows):
        html.append("<tr>")
        for cell in row:
            tag = "th" if i == 0 else "td"
            html.append(f"<{tag}>{cell}</{tag}>")
        html.append("</tr>")

    html.append("</table>")
    html.append("</body></html>")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

    print(f"Generated: {output_file}")


def main():
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".csv"):
            convert_csv_to_html(os.path.join(INPUT_DIR, file))

if __name__ == "__main__":
    main()
