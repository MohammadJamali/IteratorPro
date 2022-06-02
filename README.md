# Iterator Pro

An iterator with extra capabilities: combining multiple iterators, looping from the beginning, never calling StopIteration and return default instead, thread-safe and multithread consumer support, and shutdown()


## Examples

```python
def test(self):
    expected_result = [0, 1, 2, 3, 4, 5, 6, 7, 8, 'some data', 9, 10, 11]
    
    result = []
    
    iter_pro = IteratorPro()
    iterator = iter(iter_pro)
    
    iter_pro.insert(range(3))  # returns: 'xtwu'
    
    # result = [('xtwu', 0), ('xtwu', 1)]
    result += [next(iterator) for _ in range(2)]
    
    iter_pro.insert(range(3, 6))  # returns: 'oiom'
    
    # result = [..., ('xtwu', 2), ('oiom', 3), ('oiom', 4)]
    result += [next(iterator) for _ in range(3)]
    
    iter_pro.insert(range(6, 9))  # returns: 'dkty'
    iter_pro.insert('some data', solid_object=True)  # returns: 'cpkp'
    iter_pro.insert(range(9, 12))  # returns: 'aehu'
    
    # result = [ ... ('wnmq', 5), ('dkty', 6), ('dkty', 7), ('dkty', 8), ('cpkp', 'some data'), ('aehu', 9), ('aehu', 10), ('aehu', 11)]
    result += [next(iterator) for _ in range(8)]
    
    # result = [0, 1, 2, 3, 4, 5, 6, 7, 8, 'some data', 9, 10, 11]
    result = list(map(itemgetter(1), result))
    
    self.assertEqual(expected_result, result)
```

**Explanation**

- First, `IteratorPro` is being created by `iter_pro = IteratorPro()`.
- The functionality is available through the class itself, but you need to get the iterator to start using it, this can
  be done using `iterator = iter(iter_pro)`.
- To add an iterator to the queue, you can use `iter_pro.insert(...)`. it adds the provided iterator to the queue that 
  the root iterator will use to iterate.
- To add a value between iterators you can use `iter_pro.insert('some data', solid_object=True)`, this function will add
  the provided value to the root iterator `as is`, you can also add another iterator to the list as a value that will
  not be iterated using this function. As an example, `iter_pro.insert(range(6, 8), solid_object=True)` will
  return `range(6, 8)` instead of [6, 7].
- Once an iterator is being added by `.insert(...)`, it returns a randomly generated id (if not provided by the arguments)
  which you can use to find out when the value of a specific iterator is being iterated. for example when you add an
  iterator named `X`, and it returns `'cpkp'`, you can use this string as a key to finding out when the values of the `X`
  is being iterated.

## Credits

Mohammad Jamali (mohammadjamalid@gmail.com)

## Licence

Copyright (c) 2012-2022 Scott Chacon and others

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.