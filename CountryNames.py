import pycountry

def get_countryName(country_code):
    """Returns the full country name for a given ISO 3166-1 alpha-2 country code."""
    try:
        country = pycountry.countries.get(alpha_2=country_code)
        
        if country:
            return country.name
        else:
            return f"Unknown Country ({country_code})"
    
    except KeyError:
        return f"Error: Country code '{country_code}' not recognized."