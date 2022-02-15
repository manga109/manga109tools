import cchardet
from pathlib import Path
import pytest

import manga109api


class ContentTestBase:
    @pytest.fixture(scope="module")
    def annotations(self, root_dir: Path, target_annot: str) -> list:
        """Annotations parsed by a manga109 parser

        Args:
            root_dir (Path): root directory of manga109 data
            target_annot (str): directory name of annotation

        Returns:
            list:
            list of annotation per book obtained by a manga109 parser
        """
        parser = manga109api.Parser(root_dir)
        return [
            parser.get_annotation(book, annotation_type=target_annot)
            for book in parser.books
        ]

    def test_book_title(self, annotations: list, root_dir: Path) -> None:
        """The titles are the same with the titles in books.txt.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
            root_dir (Path): root directory of manga109 data
        """
        parser = manga109api.Parser(root_dir)
        for (annotation, book) in zip(annotations, parser.books):
            assert annotation["title"] == book

    def test_page_index(self, annotations: list) -> None:
        """The page index are sequential.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
        """
        for annotation in annotations:
            for i, page in enumerate(annotation["page"]):
                assert page["@index"] == i


class FormatTestBase:
    def test_books_txt(self, root_dir: Path, target_annot: str) -> None:
        """The titles in books.txt are the same with the file names of XML files without file extension.

        Args:
            root_dir (Path): root directory of manga109 data
            target_annot (str): directory name of annotation
        """
        book_path: Path = root_dir / "books.txt"
        assert book_path.exists()

        with book_path.open("rt", encoding="utf-8") as f:
            books = [line.rstrip() for line in f]

        for book in books:
            assert (root_dir / target_annot / book).with_suffix(".xml").exists()

    def test_file_type(self, root_dir: Path, target_annot: str) -> None:
        """The XML files of annotations use UTF-8 codec and LF as a new line command.

        Args:
            root_dir (Path): root directory of manga109 data
            target_annot (str): directory name of annotation
        """
        paths = sorted((root_dir / target_annot).iterdir())

        for path in paths:
            # UTF-8
            with path.open("rb") as f:
                text_bytes: bytes = f.read()
            assert cchardet.detect(text_bytes)["encoding"] == "UTF-8"

            # newline is LF, not CR (\r) or CRLF (\r\n)
            text_str: str = text_bytes.decode("utf-8")
            assert "\r" not in text_str
