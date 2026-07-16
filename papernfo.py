from pypdf import PdfReader

pdf = PdfReader("paper.pdf")

page_number = 1   # jis page ke words chahiye

text = pdf.pages[page_number - 1].extract_text()

words = len(text.split())

print("Page:", page_number)
print("Words:", words)