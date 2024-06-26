class BibEntry:
    """###One single bibliographical entry
    Contains:
    * authors - a string of all author names
    * title - the title of the document
    * source - the publisher of the document
    * physical_desc - the physical description of the document
    * tome - the tome information of the document

    Methods:
    * __repr__ - to print
    * __str__ - convert the entire bibliographic entry to a string
    """

    def __init__(self, authors: str, title: str, source: str, physical_desc: str, tome: str) -> None:
        self.authors = authors
        self.title = title
        self.source = source
        self.physical_desc = physical_desc
        self.tome = tome

    def __repr__(self):
        """Print the contents of the entry, testing function"""
        return f"{self.authors} {self.title} // {self.source} {self.physical_desc} ! {self.tome}"

    def __str__(self):
        """Return the contents of the entry."""
        return f"{self.authors} {self.title} // {self.source} {self.physical_desc} ! {self.tome}"
