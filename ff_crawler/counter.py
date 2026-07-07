from bs4 import BeautifulSoup


def count_phrase(html: str, phrase: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(" ")
    text = text.replace("\x00", "")
    text = " ".join(text.split())
    return text.lower().count(phrase.lower().strip())
