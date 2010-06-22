from django.test import TestCase
from dvcs.models import Change, Document

class DocumentModelTests(TestCase):

    def assertTextEqual(self, given, expected):
        return self.assertEqual(given, expected,
            "Expected '''%s'''\n differs from text: '''%s'''" % (expected, given)
        )

    def test_empty_file(self):
        doc = Document.objects.create(name=u"Sample Document")
        self.assert_(doc.head is not None)
        self.assertEqual(doc.materialize(), u"")

    def test_single_commit(self):
        doc = Document.objects.create(name=u"Sample Document")
        doc.commit(text=u"Ala ma kota", description="Commit #1")
        self.assert_(doc.head is not None)
        self.assertEqual(doc.change_set.count(), 2)
        self.assertEqual(doc.materialize(), u"Ala ma kota")

    def test_chained_commits(self):
        doc = Document.objects.create(name=u"Sample Document")
        c1 = doc.commit(description="Commit #1", text=u"""
            Line #1
            Line #2 is cool
        """)
        c2 = doc.commit(description="Commit #2", text=u"""
            Line #1
            Line #2 is hot
        """)
        c3 = doc.commit(description="Commit #3", text=u"""
            Line #1
            ... is hot
            Line #3 ate Line #2
        """)
        self.assert_(doc.head is not None)
        self.assertEqual(doc.change_set.count(), 4)

        self.assertEqual(doc.materialize(), u"""
            Line #1
            ... is hot
            Line #3 ate Line #2
        """)
        self.assertEqual(doc.materialize(version=c3), u"""
            Line #1
            ... is hot
            Line #3 ate Line #2
        """)
        self.assertEqual(doc.materialize(version=c2), u"""
            Line #1
            Line #2 is hot
        """)
        self.assertEqual(doc.materialize(version=c1), """
            Line #1
            Line #2 is cool
        """)


    def test_parallel_commit_noconflict(self):
        doc = Document.objects.create(name=u"Sample Document")
        self.assert_(doc.head is not None)
        base = doc.head
        base = doc.commit(description="Commit #1", text=u"""
            Line #1
            Line #2
""")

        c1 = doc.commit(description="Commit #2", text=u"""
            Line #1 is hot
            Line #2
""", parent=base)
        self.assertTextEqual(c1.materialize(), u"""
            Line #1 is hot
            Line #2
""")
        c2 = doc.commit(description="Commit #3", text=u"""
            Line #1
            Line #2
            Line #3
""", parent=base)
        self.assertEqual(doc.change_set.count(), 5)
        self.assertTextEqual(doc.materialize(), u"""
            Line #1 is hot
            Line #2
            Line #3
""")

    def test_parallel_commit_conflict(self):
        doc = Document.objects.create(name=u"Sample Document")
        self.assert_(doc.head is not None)
        base = doc.head
        base = doc.commit(description="Commit #1", text=u"""
Line #1
Line #2
Line #3
""")

        c1 = doc.commit(description="Commit #2", text=u"""
Line #1
Line #2 is hot
Line #3
""", parent=base)
        c2 = doc.commit(description="Commit #3", text=u"""
Line #1
Line #2 is cool
Line #3
""", parent=base)
        self.assertEqual(doc.change_set.count(), 5)
        self.assertTextEqual(doc.materialize(), u"""
Line #1
<<<<<<<
Line #2 is hot
=======
Line #2 is cool
>>>>>>>
Line #3
""")

