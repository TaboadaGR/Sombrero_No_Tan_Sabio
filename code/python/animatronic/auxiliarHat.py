
def raw_names_to_expected_format(raw_names: dict) -> dict:
    """
    Convierte el formato raw en el formato esperado, es decir,
    un diccionario donde cada clave es el nombre del usuario
    y contiene una tupla con la casa y la mesa
    """

    result: dict = dict()
    for element in raw_names['nombres_y_mesas']:
        result.update({
            element.get('nombre'): (element.get('casa'), element.get('mesa'))
        })
    
    return result