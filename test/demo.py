import ash

TEXT = """
You can find this in the sporting goods department. That's right, this sweet baby was
made in Grand Rapids, Michigan. Retails for about doi: 10.10995/walnutstock.
That's right. "Short Smart: Shop S-Mart!"
"""
db = ash.RetractionDatabase("./test/mock/rw_database.csv")
paper = ash.Paper(TEXT, mime_type="text/plain")
print(paper.report(db, validate_dois=False))
