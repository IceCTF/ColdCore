import pycountry

TShirts = [
    "XS",
    "S",
    "M",
    "L",
    "XL",
    "XXL"
]

Backgrounds = [
    ("elementary", "Elementary School Student"),
    ("high", "High School Student"),
    ("university", "University Student"),
    ("teacher", "Teacher"),
    ("professional", "Security Professional"),
    ("hobbyist", "CTF Hobbyist(non-student)"),
    ("other", "Other")
]

BackgroundKeys = [x[0] for x in Backgrounds]

Countries = [(country.alpha_3, country.name) for country in pycountry.countries]
Countries = (sorted(Countries, key=lambda x: "0" if x[1] == "Iceland" else x[1]))
CountryKeys = [x[0] for x in Countries]


def genoption(arr, selected=None, header=None):
    s = ""
    if header is not None:
        s += header
    for val in arr:
        if isinstance(val, tuple):
            val, name = val
        else:
            name = val
        if selected is not None and val == selected:
            s += ('<option value="%s" selected>%s</option>' % (val, name))
        else:
            s += ('<option value="%s">%s</option>' % (val, name))
    return s
