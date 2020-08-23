def removeSpecialFromPrice(textInput: str) -> str:
    return textInput.replace(".", "").replace(",", ".").replace("€", "")

