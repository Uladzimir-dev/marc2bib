"""Here are all currently defined tag-functions."""

import re
from typing import Optional

from pymarc import Record  # type: ignore


def get_address(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd25x28x.html
    fields = record.get_fields("260", "264")
    if fields:
        field = fields[0]
        return field["a"].replace("[", "").replace("]", "").rstrip(": ")
    else:
        return None


def get_author(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd1xx.html
    # https://www.loc.gov/marc/bibliographic/bd400.html
    # https://www.loc.gov/marc/bibliographic/bd600.html
    # https://www.loc.gov/marc/bibliographic/bd800.
    authors = []
    field = record["100"]
    if field:
      if "a" in field:
        name = field["a"]
        if field.indicator1 == "0":
          parts = name.split(", ")
          name = f"{parts[1]}, {parts[0]}"
        authors.append(name)
    fields = record.get_fields("400", "600", "700", "800")
    if fields:
      for field in fields:
        if field:
          if "e" in field:
            role = field["e"]
            if role.lower() in ["author", "автор", "авт.", "compiled by"]:
              name = field["a"]
              if field.indicator1 == "0":
                parts = name.split(", ")
                name = f"{parts[1]}, {parts[0]}"
              authors.append(name)
    return " and ".join(authors) if authors else None


def get_edition(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd250.html
    fields = record.get_fields("250")
    for field in fields:
      edition = field["a"] if "a" in field else ""
      additional_info  = field["b"] if "b" in field else ""
      return f"{edition} {additional_info}".strip()
    else:
      return None


def get_editor(record: Record) -> Optional[str]:
    editors = []
    fields = record.get_fields("100", "400", "600", "700", "800")
    if fields:
      for field in fields:
        if field:
          if "e" in field:
            role = field["e"]
            if role.lower() in ["editor", "редактор", "ed.", "научный редактор", "Ред."]:
              name = field["a"]
              if field.indicator1 == "0":
                parts = name.split(", ")
                name = f"{parts[1]}, {parts[0]}"
              editors.append(name)
    return " and ".join(editors) if editors else ""


def get_publisher(record: Record) -> Optional[str]:
  fields = record.get_fields("260", "264")
  if fields:
    for field in fields:
      if field and "b" in field:
        return field["b"]
  return None
         

def get_title(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd245.html
    fields = record.get_fields("245")
    for field in fields:
      title = field["a"] if "a" in field else ""
      subtitle = field["b"] if "b" in field else ""
      return f"{title} {subtitle}".strip()
    else:
      return None


def get_subtitle(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd245.html
    field = record["245"]
    if field:
        return field["b"]
    else:
        return None


def get_year(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd25x28x.html
  fields = record.get_fields("260", "264")
  if fields:
    for field in fields:
      if field and "c" in field:
        return field["c"].lstrip("@")
  return None


def get_volume(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd300.html
    as_roman_numeral_re = r"^\[?([mdclxvi]+)\]?,"
    with_abbrev_re = r"\b(?:[тv]\.?|Tom|Volume|Vol\.?)\s*([0-9]+)"
    volume_number_pa = re.compile(r"|".join((as_roman_numeral_re, with_abbrev_re)))
    volume = ""
    volume1 = ""
    fields = record.get_fields("300")
    if fields and fields[0] and "a" in fields[0]:
      m = volume_number_pa.search(fields[0]["a"], re.IGNORECASE)
      if m:
        return m.group(1) or m.group(2)
    fields = record.get_fields("490")
    if fields and fields[0] and "a" in fields[0]:
      volume = fields[0]["v"] if "v" in fields[0] else ""
      if fields[0].indicator1 == 0:
        return volume
    fields = record.get_fields("830")
    if fields and fields[0]:
      volume1 = fields[0]["v"] if "v" in fields[0] else ""
    return f"{volume} {volume1}".strip();


def get_volumes(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd300.html
    fields = record.get_fields("300")
    for field in fields:
      if field:
        m = re.search(r"([0-9]+)\s[v\s.?|volumes|T\s.?|Тома]", field["a"], re.IGNORECASE)
        return m.group(1) if m else ""
    else:
        return ""


def get_pages(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd300.html
    fields = record.get_fields("300")
    if fields and fields[0]:
      m = re.search(r"\[?(([0-9]+-)?[0-9]+)\]?\s?[pс]\.?", fields[0]["a"])
      return m.group(1) if m else None
    else:
        return ""


def get_note(record: Record) -> Optional[str]:
    fields = record.get_fields("500", "504", "505")
    notes =[]
    if fields:
      for field in fields:
        if "a" in field:
          notes.append(field["a"])
    return "; ".join(notes) if notes else ""


def get_series(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd490.html
    serie = ""
    serie1 = ""
    fields = record.get_fields("490")
    if fields and fields[0]:
      serie = fields[0]["a"] if "a" in fields[0] else ""
      if fields[0].indicator1 == 0:
        return serie
    fields = record.get_fields("830")
    if fields and fields[0]:
      serie1 = fields[0]["a"] if "a" in fields[0] else ""
    return f"{serie} {serie1}".strip();
      

def get_summary(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd520.html
    field_520 = record.get_fields("520")
    if field_520:
      # Извлекаем основную аннотацию ($a) и расширение ($b), если они есть
      annotation = field_520["a"] if "a" in field_520 else ""
      additional_info = field_520["b"] if "b" in field_520 else ""
      return f"{annotation} {additional_info}".strip()
    else:
      return ""


def get_isbn(record: Record) -> Optional[str]:
    # https://www.loc.gov/marc/bibliographic/bd520.html
    isbns = ""
    fields_020 = record.get_fields("020")
    for field in fields_020:
        if "a" in field:  # Основной ISBN
            isbns = field["a"].strip()
        if "z" in field:  # Недействительный ISBN
            isbns.join(f"Invalid: {field['z'].strip()}")
    return isbns