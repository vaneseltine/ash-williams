def rtf_to_text(text: str, encoding: str = ..., errors: str = ...) -> str:
    """Converts the rtf text to plain text.

    Parameters
    ----------
    text : str
        The rtf text
    encoding : str
        Input encoding which is ignored if the rtf file contains an explicit codepage directive,
        as it is typically the case. Defaults to `cp1252` encoding as it the most commonly used.
    errors : str
        How to handle encoding errors. Default is "strict", which throws an error. Another
        option is "ignore" which, as the name says, ignores encoding errors.

    Returns
    -------
    str
        the converted rtf text as a python unicode string
    """
    ...
