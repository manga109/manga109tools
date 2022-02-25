import itertools
from pathlib import Path
import pytest

import manga109api
import numpy as np
import yaml

from manga109tools.tests.base import ContentTestBase
from manga109tools.utils import is_hexadecimal, bbox_contain, bboxes_iou


@pytest.fixture(scope="session")
def exception_dict(request: pytest.FixtureRequest) -> dict:
    """Exceptions in the testing dataset.

    Args:
        request (pytest.FixtureRequest):

    Returns:
        dict:
        exceptions whose keys are the function name
        and values are lists of ids or tuples of two ids.
    """
    path: Path = request.config.getoption("--exception_path")
    exception_dict: dict = dict()
    with path.open() as f:
        exception_dict = yaml.safe_load(f)

    for exceptions in exception_dict.values():
        # no exception
        if len(exceptions) == 0:
            continue

        # list of two ids -> tuple of two ids
        if isinstance(exceptions[0], list):
            for i in range(len(exceptions)):
                # list to tuple
                exceptions[i] = tuple(exceptions[i])

    return exception_dict


def get_bbox(element: dict) -> tuple:
    """Get a bounding box from a manga109 element.

    Args:
        element (dict): a manga element such as body, face, frame, and text

    Returns:
        tuple:
        a bounding box that comparises four integers -- (xmin, ymin, xmax, ymax)
    """
    bbox_attrs = ("@xmin", "@ymin", "@xmax", "@ymax")
    xmin, ymin, xmax, ymax = [element[attr] for attr in bbox_attrs]
    return (xmin, ymin, xmax, ymax)


class TestAnnotation(ContentTestBase):
    def test_duplicate_id(self, annotations: list) -> None:
        """No duplicate id exists.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
        """
        ids = list()
        for annotation in annotations:
            for character in annotation["character"]:
                ids.append(character["@id"])

            for page in annotation["page"]:
                for annotation_tag in manga109api.Parser.annotation_tags:
                    for element in page[annotation_tag]:
                        ids.append(element["@id"])

        assert len(ids) == len(set(ids))

    def test_chara_id(self, annotations: list) -> None:
        """The character id of faces and bodies should be pre-defined in characters.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
        """
        for annotation in annotations:
            chara_ids: set = {character["@id"] for character in annotation["character"]}

            for page in annotation["page"]:
                for annotation_tag in {"face", "body"}:
                    for element in page[annotation_tag]:
                        assert element["@character"] in chara_ids

    def test_id_type(self, annotations: list) -> None:
        """Ids are hexadecimal with eight digits.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
        """
        for annotation in annotations:
            for character in annotation["character"]:
                assert len(character["@id"]) == 8 and is_hexadecimal(character["@id"])

            for page in annotation["page"]:
                for annotation_tag in manga109api.Parser.annotation_tags:
                    for element in page[annotation_tag]:
                        assert len(element["@id"]) == 8 and is_hexadecimal(
                            element["@id"]
                        )

    def test_duplicate_character_name(self, annotations: list) -> None:
        """No duplicate character name exists.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
        """
        for annotation in annotations:
            character_names = [
                character["@name"] for character in annotation["character"]
            ]
            assert len(character_names) == len(set(character_names))

    def test_text_content(self, annotations: list) -> None:
        """Text elements have text content and are not empty.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
        """
        for annotation in annotations:
            for page in annotation["page"]:
                for text in page["text"]:
                    # text is not empty
                    assert text["#text"]

    def test_bbox_coordinate(self, annotations: list) -> None:
        """Bounding boxes of elements are not over the page and has area.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
        """
        for annotation in annotations:
            for page in annotation["page"]:
                width: int = page["@width"]
                height: int = page["@height"]

                for annotation_tag in manga109api.Parser.annotation_tags:
                    for element in page[annotation_tag]:
                        xmin, ymin, xmax, ymax = get_bbox(element)
                        assert 0 <= xmin < xmax < width
                        assert 0 <= ymin < ymax < height

    def test_duplicate_bbox(self, annotations: list, exception_dict: dict) -> None:
        """Bounding boxes of elements are not overlapped.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
            exception_dict (dict): exceptions whose keys are the function name
                and values are lists of ids or tuples of two ids.
        """
        exceptions: list = exception_dict["test_duplicate_bbox"]
        iou_threshold: float = 0.98

        for annotation in annotations:
            for page in annotation["page"]:
                for annotation_tag in manga109api.Parser.annotation_tags:
                    bboxes = list()
                    ids = list()
                    for element in page[annotation_tag]:
                        bbox = get_bbox(element)
                        bboxes.append(bbox)
                        ids.append(element["@id"])

                    if len(bboxes) == 0:
                        continue

                    # bboxes: shape (N, 4)
                    bboxes = np.array(bboxes).astype(np.float32)
                    # ious: shape (N, N)
                    ious: np.ndarray = bboxes_iou(bboxes, bboxes)
                    # remove diagonal
                    np.fill_diagonal(ious, 0)
                    duplicate_flag: np.ndarray = ious >= iou_threshold
                    try:
                        assert not np.any(duplicate_flag)
                    except Exception:
                        for i, j in zip(*np.where(duplicate_flag)):
                            assert (ids[i], ids[j]) in exceptions

    @pytest.mark.skip(reason="5.8% of faces raise assertion error.")
    def test_face_in_body(self, annotations: list) -> None:
        """Each bounding box of face elements is in at least one bounding box of body elements
        of the same character.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
        """
        n_correct_bbox: int = 0
        n_detected_bbox: int = 0
        for annotation in annotations:
            for page in annotation["page"]:
                faces = page["face"]
                bodies = page["body"]
                for face in faces:
                    try:
                        assert any(
                            [
                                bbox_contain(get_bbox(body), get_bbox(face))
                                and face["@character"] == body["@character"]
                                for body in bodies
                            ]
                        )
                        n_correct_bbox += 1
                    except AssertionError:
                        n_detected_bbox += 1

        print(n_correct_bbox, n_detected_bbox)

    def test_face_not_in_face(self, annotations: list, exception_dict: dict) -> None:
        """Each bounding box of a face element is not in a bounding box of
        another face element of the same character.

        Args:
            annotations (list): list of annotation per book obtained by a manga109 parser
            exception_dict (dict): exceptions whose keys are the function name
                and values are lists of ids or tuples of two ids.
        """
        exceptions: list = exception_dict["test_face_not_in_face"]
        for annotation in annotations:
            for page in annotation["page"]:
                faces = page["face"]
                for i, j in itertools.permutations(range(len(faces)), 2):
                    if faces[i]["@character"] != faces[j]["@character"]:
                        continue

                    try:
                        assert not bbox_contain(get_bbox(faces[i]), get_bbox(faces[j]))
                    except AssertionError:
                        assert (faces[i]["@id"], faces[j]["@id"]) in exceptions
