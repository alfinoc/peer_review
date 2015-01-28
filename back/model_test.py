import unittest
import model

DUMMY_HASH = {
   'key1': 'abcde',
   'key2': 'fghij'
}

class ModelTest(unittest.TestCase):
   def setUp(self):
      pass

   def tearDown(self):
      pass

   # basic store entry functionality:
   # suffix, key, loadHash, setId
   def test_basicStoreEntryTest(self):
      s = model.StoreEntry()
      with self.assertRaises(NotImplementedError):
         s.suffix()
      with self.assertRaises(NotImplementedError):
         s.key()
      s.loadHash(DUMMY_HASH)
      self.assertEqual(s.key1, DUMMY_HASH['key1'])
      self.assertEqual(s.key2, DUMMY_HASH['key2'])
      s.setId(1)
      self.assertEqual(1, s.getId())
      s.setId('abc')
      self.assertEqual('abc', s.getId())

   def test_courseModel(self):
      pass

if __name__ == '__main__':
   unittest.main()