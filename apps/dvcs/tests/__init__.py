from nose.tools import *
from django.test import TestCase
from dvcs.models import Document


class ADocument(Document):
    class Meta:
        app_label = 'dvcs'


class DocumentModelTests(TestCase):

    def assertTextEqual(self, given, expected):
        return self.assertEqual(given, expected,
            "Expected '''%s'''\n differs from text: '''%s'''" % (expected, given)
        )

    def test_empty_file(self):
        doc = ADocument.objects.create()
        self.assertTextEqual(doc.materialize(), u"")

    def test_single_commit(self):
        doc = ADocument.objects.create()
        doc.commit(text=u"Ala ma kota", description="Commit #1")
        self.assertTextEqual(doc.materialize(), u"Ala ma kota")

    def test_chained_commits(self):
        doc = ADocument.objects.create()
        text1 = u"""
            Line #1
            Line #2 is cool
        """
        text2 = u"""
            Line #1
            Line #2 is hot
        """
        text3 = u"""
            Line #1
            ... is hot
            Line #3 ate Line #2
        """

        c1 = doc.commit(description="Commit #1", text=text1)
        c2 = doc.commit(description="Commit #2", text=text2)
        c3 = doc.commit(description="Commit #3", text=text3)

        self.assertTextEqual(doc.materialize(), text3)
        self.assertTextEqual(doc.materialize(change=c3), text3)
        self.assertTextEqual(doc.materialize(change=c2), text2)
        self.assertTextEqual(doc.materialize(change=c1), text1)

    def test_parallel_commit_noconflict(self):
        doc = ADocument.objects.create()
        text1 = u"""
            Line #1
            Line #2
        """
        text2 = u"""
            Line #1 is hot
            Line #2
        """
        text3 = u"""
            Line #1
            Line #2
            Line #3
        """
        text_merged = u"""
            Line #1 is hot
            Line #2
            Line #3
        """

        base = doc.commit(description="Commit #1", text=text1)
        c1 = doc.commit(description="Commit #2", text=text2)
        commits = doc.change_set.count()
        c2 = doc.commit(description="Commit #3", text=text3, parent=base)
        self.assertEqual(doc.change_set.count(), commits + 2,
            u"Parallel commits should create an additional merge commit")
        self.assertTextEqual(doc.materialize(), text_merged)

    def test_parallel_commit_conflict(self):
        doc = ADocument.objects.create()
        text1 = u"""
            Line #1
            Line #2
            Line #3
        """
        text2 = u"""
            Line #1
            Line #2 is hot
            Line #3
        """
        text3 = u"""
            Line #1
            Line #2 is cool
            Line #3
        """
        text_merged = u"""
            Line #1
<<<<<<<
            Line #2 is hot
=======
            Line #2 is cool
>>>>>>>
            Line #3
        """
        base = doc.commit(description="Commit #1", text=text1)
        c1 = doc.commit(description="Commit #2", text=text2)
        commits = doc.change_set.count()
        c2 = doc.commit(description="Commit #3", text=text3, parent=base)
        self.assertEqual(doc.change_set.count(), commits + 2,
            u"Parallel commits should create an additional merge commit")
        self.assertTextEqual(doc.materialize(), text_merged)


    def test_multiple_parallel_commits(self):
        text_a1 = u"""
            Line #1

            Line #2

            Line #3
            """
        text_a2 = u"""
            Line #1 *

            Line #2

            Line #3
            """
        text_b1 = u"""
            Line #1

            Line #2 **

            Line #3
            """
        text_c1 = u"""
            Line #1

            Line #2

            Line #3 ***
            """
        text_merged = u"""
            Line #1 *

            Line #2 **

            Line #3 ***
            """


        doc = ADocument.objects.create()
        c1 = doc.commit(description="Commit A1", text=text_a1)
        c2 = doc.commit(description="Commit A2", text=text_a2, parent=c1)
        c3 = doc.commit(description="Commit B1", text=text_b1, parent=c1)
        c4 = doc.commit(description="Commit C1", text=text_c1, parent=c1)
        self.assertTextEqual(doc.materialize(), text_merged)
