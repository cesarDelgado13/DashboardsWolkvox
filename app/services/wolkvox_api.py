
async def ejecutar_accion(accion):

    if accion == "create_campaign":
        return "1"
    elif accion == "load_campaign":
        return "2"
    else:
        return "3"