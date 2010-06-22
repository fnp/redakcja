from django.test import TestCase
from dvcs.models import Change, Document
from django.contrib.auth.models import User

class DocumentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("tester", "tester@localhost.local")

    def assertTextEqual(self, given, expected):
        return self.assertEqual(given, expected,
            "Expected '''%s'''\n differs from text: '''%s'''" % (expected, given)
        )

    def test_empty_file(self):
        doc = Document.objects.create(name=u"Sample Document", creator=self.user)
        self.assert_(doc.head is not None)
        self.assertEqual(doc.materialize(), u"")

    def test_single_commit(self):
        doc = Document.objects.create(name=u"Sample Document", creator=self.user)
        doc.commit(text=u"Ala ma kota", description="Commit #1", author=self.user)
        self.assert_(doc.head is not None)
        self.assertEqual(doc.change_set.count(), 2)
        self.assertEqual(doc.materialize(), u"Ala ma kota")

    def test_chained_commits(self):
        doc = Document.objects.create(name=u"Sample Document", creator=self.user)
        c1 = doc.commit(description="Commit #1", text=u"""
            Line #1
            Line #2 is cool
        """, author=self.user)
        c2 = doc.commit(description="Commit #2", text=u"""
            Line #1
            Line #2 is hot
        """, author=self.user)
        c3 = doc.commit(description="Commit #3", text=u"""
            Line #1
            ... is hot
            Line #3 ate Line #2
        """, author=self.user)
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
        doc = Document.objects.create(name=u"Sample Document", creator=self.user)
        self.assert_(doc.head is not None)
        base = doc.head
        base = doc.commit(description="Commit #1", text=u"""
            Line #1
            Line #2
""", author=self.user)

        c1 = doc.commit(description="Commit #2", text=u"""
            Line #1 is hot
            Line #2
""", parent=base, author=self.user)
        self.assertTextEqual(c1.materialize(), u"""
            Line #1 is hot
            Line #2
""")
        c2 = doc.commit(description="Commit #3", text=u"""
            Line #1
            Line #2
            Line #3
""", parent=base, author=self.user)
        self.assertEqual(doc.change_set.count(), 5)
        self.assertTextEqual(doc.materialize(), u"""
            Line #1 is hot
            Line #2
            Line #3
""")

    def test_parallel_commit_conflict(self):
        doc = Document.objects.create(name=u"Sample Document", creator=self.user)
        self.assert_(doc.head is not None)
        base = doc.head
        base = doc.commit(description="Commit #1", text=u"""
Line #1
Line #2
Line #3
""", author=self.user)

        c1 = doc.commit(description="Commit #2", text=u"""
Line #1
Line #2 is hot
Line #3
""", parent=base, author=self.user)
        c2 = doc.commit(description="Commit #3", text=u"""
Line #1
Line #2 is cool
Line #3
""", parent=base, author=self.user)
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

    def test_multiply_parallel_commits(self):
        doc = Document.objects.create(name=u"Sample Document", creator=self.user)
        self.assert_(doc.head is not None)
        c1 = doc.commit(description="Commit A1", text=u"""
Line #1

Line #2

Line #3
""", author=self.user)
        c2 = doc.commit(description="Commit A2", text=u"""
Line #1 *

Line #2

Line #3
""", author=self.user)
        c3 = doc.commit(description="Commit B1", text=u"""
Line #1

Line #2 **

Line #3
""", parent=c1, author=self.user)
        c4 = doc.commit(description="Commit C1", text=u"""
Line #1 *

Line #2

Line #3 ***
""", parent=c2, author=self.user)
        self.assertEqual(doc.change_set.count(), 7)
        self.assertTextEqual(doc.materialize(), u"""
Line #1 *

Line #2 **

Line #3 ***
""")

