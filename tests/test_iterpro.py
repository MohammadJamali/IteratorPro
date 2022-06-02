import unittest
from operator import itemgetter

from iterpro.iterpro import IteratorPro


class IteratorProTestCase(unittest.TestCase):
    def test_multi_iterator(self):
        expected_result = list(range(3)) + list(range(3, 6)) + list(range(6, 9)) + \
                          ['some data'] + list(range(9, 12))
        result = []

        iter_pro = IteratorPro()
        iterator = iter(iter_pro)

        iter_pro.insert(range(3))
        result += [next(iterator) for _ in range(2)]
        iter_pro.insert(range(3, 6))
        result += [next(iterator) for _ in range(3)]
        iter_pro.insert(range(6, 9))
        iter_pro.insert('some data', solid_object=True)
        iter_pro.insert(range(9, 12))
        result += [next(iterator) for _ in range(8)]
        result = list(map(itemgetter(1), result))  # Exclude keys

        self.assertEqual(expected_result, result)

    def test_out_of_index_fetch(self):
        expected_result = \
            list(range(3)) + \
            list(range(3, 6)) + [None] * 2 + list(range(6, 9)) + ['some data'] + list(range(9, 12)) + \
            [None] * 4
        result = []

        iter_pro = IteratorPro()
        iterator = iter(iter_pro)

        iter_pro.insert(range(3))
        result += [next(iterator) for _ in range(3)]  # 0, 1, 2
        iter_pro.insert(range(3, 6))
        result += [next(iterator) for _ in range(3)]  # 3, 4, 5
        result += [next(iterator) for _ in range(2)]  # [None] * 2
        iter_pro.insert(range(6, 9))
        iter_pro.insert('some data', solid_object=True)
        iter_pro.insert(range(9, 12))
        result += [next(iterator) for _ in range(7)]  # 6, 7, 8, 'some data', 9, 10, 11
        result += [next(iterator) for _ in range(4)]  # [None] * 4
        result = list(map(itemgetter(1), result))  # Exclude keys

        self.assertEqual(expected_result, result)

    def test_empty_fetch(self):
        expected_result = [None] * 3
        result = []

        iter_pro = IteratorPro()
        iterator = iter(iter_pro)

        result += [next(iterator) for _ in range(3)]
        result = list(map(itemgetter(1), result))  # Exclude keys

        self.assertEqual(expected_result, result)

    def test_exrta(self):
        expected_result = [0, 1, 'extra', 2, 3, 4, 'extra', 5, 'extra', 'extra', 'extra', 6, 7, 8]

        result = []

        iter_pro = IteratorPro()
        iter_pro.insert(range(9))
        iterator = iter(iter_pro)

        result += [next(iterator) for _ in range(2)]
        iter_pro.insert_extra('extra', solid_object=True)
        result += [next(iterator) for _ in range(4)]
        iter_pro.insert_extra('extra', solid_object=True)
        result += [next(iterator) for _ in range(2)]
        iter_pro.insert_extra(['extra'] * 3)
        result += [next(iterator) for _ in range(6)]

        result = list(map(itemgetter(1), result))  # Exclude keys

        self.assertEqual(expected_result, result)

    def test_loop(self):
        expected_result = list(range(3)) * 4

        result = []

        iter_pro = IteratorPro()
        iterator = iter(iter_pro.loop())
        iter_pro.insert(range(0, 3))
        result += [next(iterator) for _ in range(12)]

        result = list(map(itemgetter(1), result))  # Exclude keys

        self.assertEqual(expected_result, result)

    def test_delete_after(self):
        expected_result = [0, 1, 6, None]

        result = []

        iter_pro = IteratorPro()
        id_1 = iter_pro.insert(range(0, 3))
        id_2 = iter_pro.insert(range(3, 6))
        id_3 = iter_pro.insert(range(6, 9))
        iterator = iter(iter_pro)

        result += [next(iterator) for _ in range(2)]
        iter_pro.delete(id_1)
        iter_pro.delete(id_2)
        result += [next(iterator) for _ in range(1)]
        iter_pro.delete(id_3)
        result += [next(iterator) for _ in range(1)]

        result = list(map(itemgetter(1), result))  # Exclude keys

        self.assertEqual(expected_result, result)

    def test_delete(self):
        expected_result = [0, 1, 3, 4, 6, None]

        result = []

        iter_pro = IteratorPro()
        id_1 = iter_pro.insert(range(0, 3))
        id_2 = iter_pro.insert(range(3, 6))
        id_3 = iter_pro.insert(range(6, 9))
        iterator = iter(iter_pro)

        result += [next(iterator) for _ in range(2)]
        iter_pro.delete(id_1)
        result += [next(iterator) for _ in range(2)]
        iter_pro.delete(id_2)
        result += [next(iterator) for _ in range(1)]
        iter_pro.delete(id_3)
        result += [next(iterator) for _ in range(1)]

        result = list(map(itemgetter(1), result))  # Exclude keys

        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()
