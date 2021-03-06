import click
import frontmatter

from pathlib import Path
from sheetfu import SpreadsheetApp, Table
from slugify import slugify
from typesystem.fields import Boolean


Boolean.coerce_values.update({"n": False, "no": False, "y": True, "yes": True})


def string_to_boolean(value):
    validator = Boolean()
    value, error = validator.validate_or_error(value)

    if value is None:
        return False
    else:
        return value


def verify_http(value):
    if not value or value.startswith("http"):
        return value
    return f"https://{value}"


@click.command()
@click.option("--output-folder", default="_places")
@click.option("--sheet-app-id", envvar="LFK_GOOGLE_SHEET_APP_ID")
@click.option("--sheet-name", default="Sheet1", envvar="LFK_SHEET_NAME")
def main(sheet_app_id, output_folder, sheet_name):

    output_folder = Path(output_folder)

    sa = SpreadsheetApp(from_env=True)

    spreadsheet = sa.open_by_id(sheet_app_id)

    sheet = spreadsheet.get_sheet_by_name(sheet_name)

    # returns the sheet range that contains data values.
    data_range = sheet.get_data_range()

    table = Table(data_range, backgrounds=True)

    for item in table:
        name = item.get_field_value("name")
        slug = slugify(name)
        filename = f"{slug}.md"

        input_file = output_folder.joinpath(filename)
        if input_file.exists():
            post = frontmatter.load(input_file)
        else:
            post = frontmatter.loads("")

        place = {
            "name": name,
            "active": string_to_boolean(item.get_field_value("active")),
            "address": item.get_field_value("address"),
            "cuisine": item.get_field_value("cuisine"),
            "curbside": string_to_boolean(item.get_field_value("curbside")),
            "curbside_instructions": item.get_field_value("curbside_instructions"),
            "delivery": string_to_boolean(item.get_field_value("delivery")),
            "delivery_service_websites": item.get_field_value(
                "delivery_service_websites"
            ),
            "hours": item.get_field_value("hours"),
            "neighborhood": item.get_field_value("neighborhood"),
            "notes": item.get_field_value("notes"),
            "restaurant_phone": item.get_field_value("restaurant_phone"),
            "social": item.get_field_value("social"),
            "takeout": string_to_boolean(item.get_field_value("takeout")),
            "website": verify_http(item.get_field_value("website")),
        }
        post.content = item.get_field_value("notes")

        post.metadata.update(place)

        input_file.write_text(frontmatter.dumps(post))


if __name__ == "__main__":
    main()
