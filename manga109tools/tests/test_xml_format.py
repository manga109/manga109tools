from pathlib import Path
import pytest
import xml.etree.ElementTree as ET

from manga109tools.utils import is_int

from manga109tools.tests.base import FormatTestBase


class TestAnnotation(FormatTestBase):
    def test_tag_and_attr(self, root_dir: Path, target_annot: str) -> None:
        """test the tags and attributes in XML files.

        Args:
            root_dir (Path): root directory of manga109 data
            target_annot (str): directory name of annotation
        """
        paths = sorted((root_dir / target_annot).iterdir())

        for path in paths:
            tree: ET.ElementTree = ET.parse(path)
            root: ET.Element = tree.getroot()

            # <book> has "title" attr
            assert "title" in root.keys()

            # <book> has <characters> and <pages> elements
            characters, pages = root
            assert characters.tag == "characters"
            assert pages.tag == "pages"

            for character in characters:
                # <character> has "id" and "name" attr
                assert set(character.keys()).issuperset({"name", "id"})

            for page in pages:
                # <page> has index, height, and width
                page_attr = {"index", "height", "width"}
                set(page.keys()).issuperset(page_attr)
                assert all(is_int(page.get(attr)) for attr in page_attr)

                # <page> has <body>, <face>, <frame>, and <text> elements
                for element in page:
                    assert element.tag in {"body", "face", "frame", "text"}
                    bbox_attr = {"xmin", "ymin", "xmax", "ymax"}
                    set(element.keys()).issuperset(bbox_attr)
                    assert all(is_int(element.get(attr)) for attr in bbox_attr)

                    if element.tag in {"body", "face"}:
                        assert "character" in element.keys()

                    elif element.tag in {"text"}:
                        assert isinstance(element.text, str)
                        assert len(element.text.strip()) > 0
